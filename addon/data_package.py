import json
import logging
import os
import typing
from typing import Any, Dict
from . import cache

checksums: dict = None


def is_outdated(checksum: str, game: str) -> bool:
    return not _load_data_package_for_checksum(game, checksum)


def player_id_to_name(slot_info: dict, player_id: str) -> str:
    network_slot = slot_info.get(str(player_id))
    player_name = network_slot.get("name")
    return player_name


def item_id_to_name(slot_info: dict, item_id: str, player_id: str) -> str:
    game = slot_info.get(str(player_id)).get("game")
    checksum = checksums.get(game)
    data_package = _load_data_package_for_checksum(game, checksum)
    item_name_to_id = data_package.get("item_name_to_id")
    item_id_to_name = {v: k for k, v in item_name_to_id.items()}
    item_name = item_id_to_name.get(item_id)
    return item_name


# Copied from Archipelago/Utils.py
def store_data_package_for_checksum(game: str, data: typing.Dict[str, Any]) -> None:
    checksum = data.get("checksum")
    if checksum and game:
        if checksum != _get_file_safe_name(checksum):
            raise ValueError(f"Bad symbols in checksum: {checksum}")
        game_folder = cache.path("datapackage", _get_file_safe_name(game))
        os.makedirs(game_folder, exist_ok=True)
        try:
            with open(os.path.join(game_folder, f"{checksum}.json"), "w", encoding="utf-8-sig") as f:
                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        except Exception as e:
            logging.debug(f"Could not store data package: {e}")


# Copied from Archipelago/Utils.py
def _load_data_package_for_checksum(game: str, checksum: typing.Optional[str]) -> Dict[str, Any]:
    if checksum and game:
        if checksum != _get_file_safe_name(checksum):
            raise ValueError(f"Bad symbols in checksum: {checksum}")
        path = cache.path("datapackage", _get_file_safe_name(game), f"{checksum}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    return json.load(f)
            except Exception as e:
                logging.debug(f"Could not load data package: {e}")

    # cache does not match
    return {}


# Copied from Archipelago/Utils.py
def _get_file_safe_name(name: str) -> str:
    return "".join(c for c in name if c not in '<>:"/\\|?*')
