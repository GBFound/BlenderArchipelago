import bpy
import asyncio
import json
import os
import sys
import threading
import time
import websockets
from . import explosion, handlers, ids, progress, unlocked, thresholds

import ssl
import certifi



_ws = None
_connected = False
_loop = None
_thread = None
_pending_checks = []
_pending_checks_lock = threading.Lock()
# Use certifi's up-to-date CA bundle instead of Blender's outdated one
_ssl_context = ssl.create_default_context(cafile=certifi.where())


def connect(host: str, port: str, slot_name: str, password: str):
    global _thread
    if _thread and _thread.is_alive():
        print("[AP Client] Already connected.")
        return

    _thread = threading.Thread(
        target=_run_loop,
        args=(host, port, slot_name, password),
        daemon=True
    )
    _thread.start()


def disconnect():
    global _ws, _loop
    if _loop and _ws:
        asyncio.run_coroutine_threadsafe(_ws.close(), _loop)
    print("[AP Client] Disconnected.")


def send_check(location_id: int):
    if not _connected or _loop is None:
        with _pending_checks_lock:
            _pending_checks.append(location_id)
        return
    asyncio.run_coroutine_threadsafe(_send_checks([location_id]), _loop)


def send_goal_complete():
    asyncio.run_coroutine_threadsafe(_send_goal_complete(), _loop)


def is_connected() -> bool:
    return _connected


async def _connect(host: str, port: str, slot_name: str, password: str):
    global _ws, _connected

    if host in ("localhost", "127.0.0.1"):
        url = f"ws://{host}:{port}"
    else:
        url = f"wss://{host}:{port}"

    try:
        print(f"[AP Client] Connecting to {url}.")
        async with websockets.connect(url, compression="deflate", ssl=_ssl_context) as ws:
            _ws = ws

            await ws.send(json.dumps([{
                "cmd": "Connect",
                "password": password,
                "game": "Blender",
                "name": slot_name,
                "uuid": _get_uuid(),
                "version": {"major": 0, "minor": 6, "build": 7, "class": "Version"},
                "items_handling": 0b111,
                "tags": ["AP", "DeathLink"],
            }]))
            
            async for message in ws:
                packets = json.loads(message)
                for packet in packets:
                    await _handle_packet(packet)
                    
    except Exception as e:
        print(f"[AP Client] Connection error: {e}")
    finally:
        _ws = None
        _connected = False
        bpy.app.timers.register(_redraw_panels)


# Copied from Archipelago/Utils.py
def _get_uuid() -> str:
    common_path = _cache_path("common.json")
    try:
        with open(common_path) as f:
            common_file = json.load(f)
            uuid = common_file.get("uuid", None)
    except FileNotFoundError:
        common_file = {}
        uuid = None

    if uuid:
        return uuid

    from uuid import uuid4
    uuid = str(uuid4())
    common_file["uuid"] = uuid

    cache_folder = os.path.dirname(common_path)
    os.makedirs(cache_folder, exist_ok=True)
    with open(common_path, "w") as f:
        json.dump(common_file, f, separators=(",", ":"))
    return uuid


# Adapted from Archipelago/Utils.py (Blender's Python does not have platformdirs)
def _cache_path(*path: str) -> str:
    """Returns path to a file in the user's Archipelago cache directory."""
    if sys.platform == "win32":
        base = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Archipelago")
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Caches", "Archipelago")
    else:
        base = os.path.join(os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache")), "Archipelago")
    return os.path.join(base, *path)


async def _handle_packet(packet: dict):
    global _ws, _connected

    cmd = packet.get("cmd")

    if cmd == "RoomInfo":
        print("[AP Client] Connected to room.")

    elif cmd == "Connected":
        _connected = True

        bpy.app.timers.register(_redraw_panels)
        for item in unlocked:
            unlocked[item] = False
        _initialize_progress(packet)
        _initialize_thresholds(packet)
        if _pending_checks:
            # Shallow copy to avoid mutation during send
            await _send_checks(_pending_checks.copy())
            with _pending_checks_lock:
                checks = _pending_checks.copy()
                _pending_checks.clear()
            await _send_checks(checks)

    elif cmd == "ConnectionRefused":
        await _ws.close()
        print(f"[AP Client] Connection refused: {packet.get("errors")}")

    elif cmd == "ReceivedItems":
        await _handle_received_items(packet)

    elif cmd == "PrintJSON":
        parts = packet.get("data")
        text_parts = []
        for part in parts:
            text = part.get("text", "")
            text_parts.append(text)
        text = "".join(text_parts)
        print(f"[AP Client] {text}")

    elif cmd == "Bounced":
        tags = packet.get("tags")
        if "DeathLink" in tags:
            data = packet.get("data", {})
            source = data.get("source")
            cause = data.get("cause", f"{source} died.")
            _receive_deathlink(cause)


def _initialize_progress(packet: dict):
    slot_data = packet.get("slot_data")
    progress.min_percent = slot_data.get("min_percent")
    progress.max_percent = slot_data.get("max_percent")
    progress.goal_percent = slot_data.get("goal_percent")


def _initialize_thresholds(packet: dict):
    slot_data = packet.get("slot_data")
    server_thresholds = slot_data.get("thresholds", [])
    thresholds.clear()
    for percent in server_thresholds:
        thresholds[float(percent)] = False
    checked_locations = packet.get("checked_locations")
    sorted_thresholds = sorted(thresholds.keys())
    for i in range(len(checked_locations)):
        thresholds[sorted_thresholds[i]] = True


async def _handle_received_items(packet: dict):
    packet_index = packet.get("index")
    items = packet.get("items")

    if not items:
        return

    last_index = 0
    if bpy.context and bpy.context.scene:
        last_index = bpy.context.scene.ap_last_item_index

    if packet_index == 0:
        _clear_inventory()
        last_index = 0
    elif packet_index != last_index + 1:
        await _resync()
        return

    for i, item in enumerate(items):
        item_index = packet_index + i
        if item_index < last_index:
            continue
        
        if bpy.context and bpy.context.scene:
            bpy.context.scene.ap_last_item_index = item_index

        item_id = item.get("item")
        _unlock_item(item_id)


def _clear_inventory():
    print(f"[AP Client] Clearing inventory.")
    if bpy.context and bpy.context.scene:
        bpy.context.scene.ap_last_item_index = 0

    for item in unlocked:
        unlocked[item] = False


async def _resync():
    print(f"[AP Client] Resyncing.")
    await _send_sync()

    location_ids = []
    for i in range(len(thresholds)):
        location_name = ids.LOCATIONS[i]
        location_id = ids.LOCATION_TO_ID[location_name]
        location_ids.append(location_id)

    sent_flags = []
    for _, sent_flag in sorted(thresholds.items()):
        sent_flags.append(sent_flag)

    checked = []
    for location_id, sent_flag in zip(location_ids, sent_flags):
        if sent_flag:
            checked.append(location_id)

    if checked:
        await _send_checks(checked)


def _unlock_item(item_id: int):
    item = ids.ID_TO_ITEM.get(item_id)

    if unlocked.get(item):
        return
    
    if _activate_filler_and_traps(item):
        return
    
    unlocked[item] = True
    unlock_text = item.name.replace("_", " ").title()
    bpy.app.timers.register(_redraw_panels)
    handlers.timer_popup(f"{unlock_text} has been unlocked!")


def _activate_filler_and_traps(item: ids.Item) -> bool:
    match item:
        case ids.Item.POP_UP:
            handlers.timer_popup("your model look like poop from a butt 💔💔💔")
            return True
        case ids.Item.UNDO:
            bpy.app.timers.register(_undo)
            bpy.app.timers.register(explosion.spawn_animated_ref_image)
            handlers.timer_popup("Undo trap.")
            return True
            
    return False


def _undo():
    """
    bpy.ops.ed.undo() does not work because uhh.
    Ideally this would only undo a few steps, but the undo stack size isn't readable until Blender 5.3.
    Currently undos to the bottom of the undo history
    """
    bpy.ops.ed.undo_history(item=0)


def _receive_deathlink(cause: str):
    bpy.app.timers.register(_undo)
    bpy.app.timers.register(explosion.spawn_animated_ref_image)
    handlers.timer_popup(cause)
    print("[AP Client] Received DeathLink.")


async def send_deathlink(do: str):
    if _ws:
        await _ws.send(json.dumps([{
            "cmd": "Bounce",
            "tags": ["DeathLink"],
            "data": {
                "time": time.time(),
                "source": bpy.types.Scene.ap_slot_name,
                "cause": f"{bpy.types.Scene.ap_slot_name} hit {do}."
            }
        }]))
        print("[AP Client] Sent DeathLink.")


async def _send_sync():
    if _ws:
        await _ws.send(json.dumps([{"cmd": "Sync"}]))
        print("[AP Client] Sent sync.")


async def _send_checks(location_ids: list[int]):
    if _ws:
        await _ws.send(json.dumps([{
            "cmd": "LocationChecks",
            "locations": location_ids,
        }]))
        print(f"[AP Client] Sent checks: {location_ids}")


async def _send_goal_complete():
    if _ws:
        await _ws.send(json.dumps([{
            "cmd": "StatusUpdate",
            "status": 30  # 30 = ClientStatus.CLIENT_GOAL
        }]))
        print("[AP Client] Sent goal complete.")


def _redraw_panels():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def _run_loop(host: str, port: str, slot_name: str, password: str):
    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    _loop.run_until_complete(_connect(host, port, slot_name, password))
    _loop.close()


def register():
    bpy.types.Scene.ap_last_item_index = bpy.props.IntProperty()


def unregister():
    del bpy.types.Scene.ap_last_item_index
    if (_connected):
        disconnect()
