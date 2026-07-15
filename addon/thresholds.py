data: dict[float, bool] = {}

def initialize_thresholds(packet: dict):
    slot_data = packet.get("slot_data")
    server_thresholds = slot_data.get("thresholds", [])
    data.clear()

    for percent in server_thresholds:
        data[float(percent)] = False

    checked_locations = packet.get("checked_locations")
    sorted_thresholds = sorted(data.keys())
    for i in range(len(checked_locations)):
        data[sorted_thresholds[i]] = True
