from . import auto_load, ids

progress = {
    "percent":      0,  # Current similarity percent
    "min_percent":  20, # Checks will generate at and above this percent
    "max_percent":  50, # Checks will generate below this percent
    "goal_percent": 50, # Goal
}

unlocked = {item: False for item in ids.Item}

thresholds: dict[float, bool] = {}

auto_load.init()


def register():
    auto_load.register()
    print("\n[Blender AP] Registered.")


def unregister():
    auto_load.unregister()
    print("[Blender AP] Unregistered.")
