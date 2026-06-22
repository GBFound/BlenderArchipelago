from . import auto_load, ids
from dataclasses import dataclass


@dataclass
class Progress:
    percent:      int = 0
    min_percent:  int = 20
    max_percent:  int = 50
    goal_percent: int = 50


progress = Progress()

unlocked = {item: False for item in ids.Item if item < ids.Item.POP_UP}

thresholds: dict[float, bool] = {}

auto_load.init()


def register():
    auto_load.register()
    print("\n[Blender AP] Registered.")


def unregister():
    auto_load.unregister()
    print("[Blender AP] Unregistered.")
