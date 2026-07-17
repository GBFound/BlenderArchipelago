import bpy
import asyncio
import threading
import json
import websockets
import time
import ssl
import certifi
import random
from . import ap_data_package, cache, ids, panels, utils, progress, unlocks, thresholds

suppress_deathlink:   bool                                      = False

# _pending_checks can be accessed from both the main thread and the async thread simultaneously, so the lock prevents race conditions
_pending_checks:      list[int]                                 = []
_pending_checks_lock: threading.Lock                            = threading.Lock()

_slot_info:           dict                                      = None
_slot_id:             int                                       = None

_thread:              threading.Thread | None                   = None
_loop:                asyncio.AbstractEventLoop | None          = None
_ws:                  websockets.WebSocketClientProtocol | None = None
_connected:           bool                                      = False

# Use certifi's up-to-date CA bundle instead of Blender's outdated one
_ssl_context:         ssl.SSLContext                            = ssl.create_default_context(cafile=certifi.where())


def connect(host: str, port: str, slot_name: str, password: str):
    global _thread
    if _thread and _thread.is_alive():
        utils.queue_popup("Already connected.")
        return

    _thread = threading.Thread(
        target=_run_loop,
        args=(host, port, slot_name, password),
        daemon=True
    )
    _thread.start()


def disconnect():
    if _ws:
        asyncio.run_coroutine_threadsafe(_ws.close(), _loop)
        print("[Blender AP] Disconnected.")


def send_check(location_id: int):
    if not _connected:
        with _pending_checks_lock:
            _pending_checks.append(location_id)
        return
    asyncio.run_coroutine_threadsafe(_send_checks([location_id]), _loop)


def send_goal_complete():
    if _connected:
        asyncio.run_coroutine_threadsafe(_send_goal_complete(), _loop)


def is_connecting() -> bool:
    return _thread is not None and _thread.is_alive() and not _connected


def is_connected() -> bool:
    return _connected


def send_deathlink(do: str):
    if _connected and not suppress_deathlink:
        message = _choose_deathlink_message(do)
        asyncio.run_coroutine_threadsafe(_send_deathlink(message), _loop)
        utils.queue_popup("Sent DeathLink.")


def _choose_deathlink_message(do: str) -> str:
    message = f" hit {do}."
    message_choice = random.randint(0, 2)
    if message_choice == 2:
        message = "'s model look like poop from a butt 💔💔💔"
    return message


async def _send_deathlink(message: str):
    if _ws:
        slot_name = bpy.context.scene.ap_slot_name
        await _ws.send(json.dumps([{
            "cmd": "Bounce",
            "tags": ["DeathLink"],
            "data": {
                "time": time.time(),
                "source": slot_name,
                "cause": f"{slot_name}{message}"
            }
        }]))


def _receive_deathlink(cause: str):
    utils.schedule_undo()
    utils.queue_popup(cause)


async def _connect(host: str, port: str, slot_name: str, password: str):
    global _ws, _connected

    if host in ("localhost", "127.0.0.1"):
        url = f"ws://{host}:{port}"
    else:
        url = f"wss://{host}:{port}"

    try:
        print(f"[Blender AP] Connecting to {url}.")
        async with websockets.connect(url, compression="deflate", ssl=_ssl_context) as ws:
            _ws = ws

            await ws.send(json.dumps([{
                "cmd": "Connect",
                "password": password,
                "game": "Blender",
                "name": slot_name,
                "uuid": cache.get_uuid(),
                "version": {"major": 0, "minor": 6, "build": 7, "class": "Version"},
                "items_handling": 0b111,
                "tags": ["AP", "DeathLink"],
            }]))
            
            async for message in ws:
                packets = json.loads(message)
                for packet in packets:
                    await _handle_packet(packet)
                    
    except Exception as e:
        import traceback
        traceback.print_exc()
        utils.queue_popup(f"Connection error: {e}")
    finally:
        _ws = None
        _connected = False
        panels.schedule_redraw_panels()


async def _handle_packet(packet: dict):
    global _connected, _slot_info, _slot_id

    cmd = packet.get("cmd")

    if cmd == "RoomInfo":
        print("[Blender AP] Connected to room.")
        data_package_checksums = packet.get("datapackage_checksums")
        data_package_checksum = data_package_checksums.get("Blender")
        if not ap_data_package.is_cached() or ap_data_package.is_outdated(data_package_checksum):
            await _send_get_data_package()

    elif cmd == "DataPackage":
        print("[Blender AP] Received data package.")
        ap_data_package.save_data_package(packet.get("data"))

    elif cmd == "Connected":
        _connected = True
        _slot_info = packet.get("slot_info")
        _slot_id = packet.get("slot")
        panels.schedule_redraw_panels()
        progress.initialize_progress(packet)
        thresholds.initialize_thresholds(packet)
        if _pending_checks:
            # Shallow copy to avoid mutation during send
            with _pending_checks_lock:
                checks = _pending_checks.copy()
                _pending_checks.clear()
            await _send_checks(checks)

    elif cmd == "ConnectionRefused":
        await _ws.close()
        utils.queue_popup(f"Connection refused: {packet.get("errors")}")

    elif cmd == "ReceivedItems":
        await _handle_received_items(packet)

    elif cmd == "PrintJSON":
        if packet.get("type") == "ItemSend":
            item = packet.get("item")
            item_id = item.get("item")
            sender_id = item.get("player")
            sender_name = _player_id_to_name(sender_id)
            receiving_id = packet.get("receiving")
            receiving_name = _player_id_to_name(receiving_id)
            if _slot_id == sender_id and _slot_id == receiving_id:
                item_name = _item_id_to_name(item_id, sender_id)
                utils.queue_popup(f"Unlocked {item_name}.")
            elif _slot_id == sender_id:
                item_name = _item_id_to_name(item_id, receiving_id)
                utils.queue_popup(f"Found {item_name} for {receiving_name}.")
            elif _slot_id == receiving_id:
                item_name = _item_id_to_name(item_id, receiving_id)
                utils.queue_popup(f"Unlocked {item_name} from {sender_name}.")

    elif cmd == "Bounced":
        tags = packet.get("tags")
        if "DeathLink" in tags:
            data = packet.get("data", {})
            source = data.get("source")
            slot_name = bpy.context.scene.ap_slot_name
            if source == slot_name:
                return  # Ignore our own deathlink
            cause = data.get("cause", f"{source} died.")
            _receive_deathlink(cause)


def _player_id_to_name(player_id: str) -> str:
    network_slot = _slot_info.get(str(player_id))
    player_name = network_slot.get("name")
    return player_name


def _item_id_to_name(item_id: str, player_id: str) -> str:
    game = _slot_info.get(str(player_id)).get("game")
    data_package = ap_data_package.load_data_package()
    game_data = data_package.get("games").get(game)
    item_name_to_id = game_data.get("item_name_to_id")
    item_id_to_name = {v: k for k, v in item_name_to_id.items()}
    item_name = item_id_to_name.get(item_id)
    return item_name


async def _send_get_data_package():
    await _ws.send(json.dumps([{"cmd": "GetDataPackage"}]))


async def _handle_received_items(packet: dict):
    packet_index = packet.get("index")
    items = packet.get("items")

    if not items:
        return

    last_index = bpy.context.scene.ap_last_item_index

    if packet_index == 0:
        unlocks.clear_unlocks()
    elif packet_index != last_index + 1:
        await _resync()
        return

    for i, item in enumerate(items):
        item_index = packet_index + i
        unlocks.resyncing = item_index < last_index

        item_id = item.get("item")
        item = ids.ID_TO_ITEM.get(item_id)
        unlocks.unlock_item(item)

    _schedule_last_index(packet_index + len(items))
    unlocks.resyncing = False


def _schedule_last_index(index: int):
    bpy.app.timers.register(lambda: _set_last_index(index))


def _set_last_index(index: int):
    bpy.context.scene.ap_last_item_index = index


async def _resync():
    await _send_sync()

    checks = []
    for i, (_, checked) in enumerate(sorted(thresholds.data.items())):
        if checked:
            location_id = ids.BASE_ID + i
            checks.append(location_id)

    if checks:
        await _send_checks(checks)


async def _send_sync():
    if _ws:
        await _ws.send(json.dumps([{"cmd": "Sync"}]))


async def _send_checks(location_ids: list[int]):
    if _ws:
        await _ws.send(json.dumps([{
            "cmd": "LocationChecks",
            "locations": location_ids,
        }]))


async def _send_goal_complete():
    if _ws:
        await _ws.send(json.dumps([{
            "cmd": "StatusUpdate",
            "status": 30  # 30 = ClientStatus.CLIENT_GOAL
        }]))


def _run_loop(host: str, port: str, slot_name: str, password: str):
    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    _loop.run_until_complete(_connect(host, port, slot_name, password))
    _loop.close()


def unregister():
    if (_connected):
        disconnect()
