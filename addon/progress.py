import bpy
import threading
from . import ids, persist, redraw

_thresholds_checked: dict[float, bool] = {}
_thresholds_lock: threading.Lock = threading.Lock()

goal_percent: int = 0


def set_thresholds(thresholds: list[float], checked_locations: list[int]):
    with _thresholds_lock:
        _thresholds_checked.clear()

        for percent in thresholds:
            _thresholds_checked[float(percent)] = False

        sorted_thresholds = sorted(_thresholds_checked.keys())
        for i in range(len(checked_locations)):
            _thresholds_checked[sorted_thresholds[i]] = True


def set_goal_percent(goal: int):
    global goal_percent
    goal_percent = goal


def get_thresholds() -> dict[float, bool]:
    return _thresholds_checked


def get_thresholds_state() -> tuple[str, int, int]:
    with _thresholds_lock:
        thresholds = list(_thresholds_checked.items())
    
    checked_count = 0
    next = None
    for threshold, checked in thresholds:
        if checked:
            checked_count += 1
        elif next is None:
            next = threshold

    return next, checked_count, len(thresholds)


def get_thresholds_ids() -> list[int]:
    with _thresholds_lock:
            checks = []
            for i, (_, checked) in enumerate(sorted(_thresholds_checked.items())):
                if checked:
                    location_id = ids.BASE_ID + i
                    checks.append(location_id)
            return checks

def update_state():
    bpy.app.timers.register(_update_thresholds)
    bpy.app.timers.register(_update_goal)


def _update_thresholds():
    from . import client

    with _thresholds_lock:
        for i, (threshold, checked) in enumerate(sorted(_thresholds_checked.items())):
            if bpy.context.scene.ap_current_percent >= threshold:
                if not checked:
                    location_id = ids.BASE_ID + i
                    _thresholds_checked[threshold] = True
                    client.send_check(location_id)
            else:
                break

    redraw.panels()


def _update_goal():
    from . import client

    if not bpy.context.scene.ap_has_reached_goal and bpy.context.scene.ap_current_percent >= goal_percent and client.is_connected():
        bpy.context.scene.ap_has_reached_goal = True
        persist.ap_has_reached_goal = True
        client.send_goal_complete()
