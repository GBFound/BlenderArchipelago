import json
import os
import sys

# Copied from Archipelago/Utils.py
def get_uuid() -> str:
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
