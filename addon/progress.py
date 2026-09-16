import bpy
from . import ids, persist, redraw

thresholds_checked: dict[float, bool] = {}
goal_percent: int = 0


def set_thresholds(thresholds: list[float], checked_locations: list[int]):
    thresholds_checked.clear()

    for percent in thresholds:
        thresholds_checked[float(percent)] = False

    sorted_thresholds = sorted(thresholds_checked.keys())
    for i in range(len(checked_locations)):
        thresholds_checked[sorted_thresholds[i]] = True


def set_goal_percent(goal: int):
    global goal_percent
    goal_percent = goal


def update_state():
    bpy.app.timers.register(_update_thresholds)
    bpy.app.timers.register(_update_goal)


def _update_thresholds():
    from . import client

    for i, (threshold, checked) in enumerate(sorted(thresholds_checked.items())):
        if bpy.context.scene.ap_current_percent >= threshold:
            if not checked:
                location_id = ids.BASE_ID + i
                thresholds_checked[threshold] = True
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
