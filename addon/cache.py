import platformdirs
import os


# Copied from Archipelago/Utils.py
def path(*cache_path: str) -> str:
    """Returns path to a file in the user's Archipelago cache directory."""
    if hasattr(path, "cached_path"):
        pass
    else:
        path.cached_path = platformdirs.user_cache_dir("Archipelago", False)

    return os.path.join(path.cached_path, *cache_path)
