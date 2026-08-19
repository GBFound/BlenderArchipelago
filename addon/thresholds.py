data: dict[float, bool] = {}

def initialize_thresholds(new_thresholds: list[float], checked_locations: list[int]):
    data.clear()

    for percent in new_thresholds:
        data[float(percent)] = False

    sorted_thresholds = sorted(data.keys())
    for i in range(len(checked_locations)):
        data[sorted_thresholds[i]] = True
