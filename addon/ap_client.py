import bpy
import asyncio
import threading
import json
import websockets
import time
import ssl
import certifi
import traceback
from . import ap_data_package, ap_uuid, deathlink, explosion, handlers, ids, messages, popup, progress, redraw, thresholds, unlocks

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

# From CommonClient.py
_MAX_SIZE: int = 16 * 1024 * 1024  # 16 MB of max incoming packet size


def connect(host: str, port: str, slot_name: str, password: str):
    global _thread
    if _thread and _thread.is_alive():
        popup.enqueue("Already connected.")
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
        print("[Archipelago] Disconnected.")


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


def send_deathlink_tag_update():
    if _connected:
        asyncio.run_coroutine_threadsafe(_send_deathlink_tag_update(), _loop)


def send_deathlink(do: str):
    if not _connected:
        return
    if not deathlink.enabled:
        return
    if deathlink.suppressed:
        return
    if bpy.context.active_operator is not None:
        return  # Adjusting last operation will not send a deathlink
        """
        NOTE Using undo history to undo/redo while adjust last operation UI is on screen should still send deathlink,
        but I could not find a solution to fix this without breaking other things.
        """

    message = deathlink.choose_message(do)
    asyncio.run_coroutine_threadsafe(_send_deathlink(message), _loop)
    explosion.spawn_animated_ref_image()
    popup.enqueue("Sent DeathLink.")


def _receive_deathlink(cause: str):
    deathlink.undo()
    deathlink.enqueue_popup(cause)


async def _connect(host: str, port: str, slot_name: str, password: str, secure: bool = False):
    global _ws, _connected

    scheme = "wss" if secure else "ws"
    url = f"{scheme}://{host}:{port}"

    try:
        print(f"[Archipelago] Connecting to {url}.")
        ssl_context = _ssl_context if scheme == "wss" else None
        async with websockets.connect(
            url,
            compression="deflate",
            ssl=ssl_context,
            max_size=_MAX_SIZE,
        ) as ws:
            _ws = ws

            await ws.send(json.dumps([{
                "cmd": "Connect",
                "password": password,
                "game": "Blender",
                "name": slot_name,
                "uuid": ap_uuid.get_uuid(),
                "version": {"major": 0, "minor": 6, "build": 7, "class": "Version"},
                "items_handling": 0b111,
                "tags": ["AP"],
            }]))
            
            async for message in ws:
                packets = json.loads(message)
                for packet in packets:
                    await _handle_packet(packet)

    except websockets.InvalidMessage as e:
        if not secure:
            print(f"[Archipelago] {url} appears to require TLS, retrying as wss://.")
            await _connect(host, port, slot_name, password, secure=True)
        else:
            popup.enqueue(f"Connection error: {e}")

    except Exception as e:
        traceback.print_exc()
        popup.enqueue(f"Connection error: {e}")

    finally:
        _ws = None
        _connected = False
        redraw.panels()


async def _handle_packet(packet: dict):
    global _connected, _room_info, _slot_info, _slot_id

    cmd = packet.get("cmd")

    if cmd == "RoomInfo":
        print("[Archipelago] Connected to room.")
        data_package_checksums = packet.get("datapackage_checksums")
        for game in data_package_checksums:
            data_package_checksum = data_package_checksums.get(game)
            if ap_data_package.is_outdated(data_package_checksum, game):
                await _send_get_data_package([game])

    elif cmd == "DataPackage":
        data = packet.get("data")
        print(f"[Archipelago] Received data package for {list(data.get('games').keys())}.")
        ap_data_package.save_data_package(data)

    elif cmd == "Connected":
        _connected = True
        _slot_info = packet.get("slot_info")
        _slot_id = packet.get("slot")
        redraw.render_border()
        _initialize_from_slot_data(packet)
        unlocks.clear_unlocks()
        unlocks.set_last_index(0)
        bpy.context.scene.ap_messages.clear()
        redraw.panels()
        if _pending_checks:
            # Shallow copy to avoid mutation during send
            with _pending_checks_lock:
                checks = _pending_checks.copy()
                _pending_checks.clear()
            await _send_checks(checks)
        slot_data = packet.get("slot_data")
        deathlink.enabled = slot_data.get("death_link")
        if deathlink.enabled:
            await _send_deathlink_tag_update()

    elif cmd == "ConnectionRefused":
        await _ws.close()
        popup.enqueue(f"Connection refused: {packet.get('errors')}")

    elif cmd == "ReceivedItems":
        await _handle_received_items(packet)

    elif cmd == "PrintJSON":
        parts = packet.get("data")
        text_parts = []
        for part in parts:
            text = part.get("text", "")
            text_parts.append(text)
        text = "".join(text_parts)
        messages.add_message(text)
        printJsonType = packet.get("type")
        if printJsonType == "ItemSend":
            item = packet.get("item")
            item_id = item.get("item")
            sender_id = item.get("player")
            sender_name = ap_data_package.player_id_to_name(_slot_info, sender_id)
            receiving_id = packet.get("receiving")
            receiving_name = ap_data_package.player_id_to_name(_slot_info, receiving_id)
            if _slot_id == sender_id and _slot_id == receiving_id:
                item_name = ap_data_package.item_id_to_name(_slot_info, item_id, sender_id)
                popup.enqueue(f"Unlocked {item_name}.")
            elif _slot_id == sender_id:
                item_name = ap_data_package.item_id_to_name(_slot_info, item_id, receiving_id)
                popup.enqueue(f"Found {item_name} for {receiving_name}.")
            elif _slot_id == receiving_id:
                item_name = ap_data_package.item_id_to_name(_slot_info, item_id, receiving_id)
                popup.enqueue(f"Unlocked {item_name} from {sender_name}.")

    elif cmd == "Bounced":
        tags = packet.get("tags")
        if "DeathLink" in tags:
            data = packet.get("data", {})
            source = data.get("source")
            slot_name = bpy.context.scene.ap_slot_name
            if source == slot_name or not deathlink.enabled:
                return  # Ignore if our own deathlink or deathlink is disabled
            cause = data.get("cause", f"{source} died.")
            _receive_deathlink(cause)


def _initialize_from_slot_data(packet: dict):
    slot_data = packet.get("slot_data")
    checked_locations = packet.get("checked_locations")
    goal_percent = slot_data.get("goal_percent")
    new_thresholds = slot_data.get("thresholds")
    new_width_max = slot_data.get("progressive_render_width_max")
    new_height_max = slot_data.get("progressive_render_height_max")
    new_temp_unlock_duration_seconds = slot_data.get("full_arsenal_duration")
    progress.initialize_progress(goal_percent)
    thresholds.initialize_thresholds(new_thresholds, checked_locations)
    unlocks.initialize_unlocks(new_width_max, new_height_max, new_temp_unlock_duration_seconds)


async def _handle_received_items(packet: dict):
    packet_index = packet.get("index")
    items = packet.get("items")

    if not items:
        return

    last_index = bpy.context.scene.ap_last_item_index

    if packet_index == 0:
        unlocks.clear_unlocks()
    elif packet_index != last_index:
        await _resync()
        return

    for i, item in enumerate(items):
        item_index = packet_index + i
        unlocks.resyncing = item_index < last_index

        item_id = item.get("item")
        item = ids.ID_TO_ITEM.get(item_id)
        unlocks.unlock_item(item)

    unlocks.set_last_index(packet_index + len(items))
    unlocks.resyncing = False
    handlers.clear_locked_features()


async def _resync():
    await _send_sync()

    checks = []
    for i, (_, checked) in enumerate(sorted(thresholds.data.items())):
        if checked:
            location_id = ids.BASE_ID + i
            checks.append(location_id)

    if checks:
        await _send_checks(checks)


async def _send_get_data_package(games: list):
    if _ws:
        await _ws.send(json.dumps([{"cmd": "GetDataPackage", "games": games}]))


async def _send_sync():
    if _ws:
        await _ws.send(json.dumps([{"cmd": "Sync"}]))


async def _send_deathlink_tag_update():
    if _ws:
        tags = ["AP"]
        if deathlink.enabled:
            tags.append("DeathLink")

        await _ws.send(json.dumps([{
            "cmd": "ConnectUpdate",
            "tags": tags,
            "items_handling": 0b111,
        }]))


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
