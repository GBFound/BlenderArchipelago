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
