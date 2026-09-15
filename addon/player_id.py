import json
import os
from . import cache


# Copied from Archipelago/Utils.py
def get_uuid() -> str:
    common_path = cache.path("common.json")
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
