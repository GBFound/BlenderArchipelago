import bpy
import json
from . import persist


def save_data_package(data):
    text = bpy.data.texts.get("ap_data_package")
    if not text:
        text = bpy.data.texts.new("ap_data_package")
    text.clear()
    text.write(json.dumps(data))
    persist.ap_data_package = data


def load_data_package() -> dict:
    text = bpy.data.texts.get("ap_data_package")
    if not text:
        return {}
    return json.loads(text.as_string())


def is_cached() -> bool:
    text = bpy.data.texts.get("ap_data_package")
    if text:
        return True
    return False


def is_outdated(data_package_checksum: str) -> bool:
    local_data_package = load_data_package()
    game_data = local_data_package.get("games", {}).get("Blender")
    if game_data is None:
        return True
    local_data_package_checksum = game_data.get("checksum")
    return data_package_checksum != local_data_package_checksum

def player_id_to_name(slot_info: dict, player_id: str) -> str:
    network_slot = slot_info.get(str(player_id))
    player_name = network_slot.get("name")
    return player_name


def item_id_to_name(slot_info: dict, item_id: str, player_id: str) -> str:
    game = slot_info.get(str(player_id)).get("game")
    data_package = load_data_package()
    game_data = data_package.get("games").get(game)
    item_name_to_id = game_data.get("item_name_to_id")
    item_id_to_name = {v: k for k, v in item_name_to_id.items()}
    item_name = item_id_to_name.get(item_id)
    return item_name
