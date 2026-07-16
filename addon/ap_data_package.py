import bpy
import json


def save_data_package(data):
    text = bpy.data.texts.get("ap_data_package")
    if not text:
        text = bpy.data.texts.new("ap_data_package")
    text.clear()
    text.write(json.dumps(data))


def load_data_package() -> dict:
    text = bpy.data.texts.get("ap_data_package")
    return json.loads(text.as_string())


def is_cached() -> bool:
    text = bpy.data.texts.get("ap_data_package")
    if text:
        return True
    return False


def is_outdated(data_package_checksum: str) -> bool:
    local_data_package = load_data_package()
    game_data = local_data_package.get("games").get("Blender")
    local_data_package_checksum = game_data.get("checksum")
    return data_package_checksum != local_data_package_checksum
