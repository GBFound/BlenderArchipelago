current_percent: int = 0
goal_percent:    int = 50


def initialize_progress(packet: dict):
    global goal_percent
    slot_data = packet.get("slot_data")
    goal_percent = slot_data.get("goal_percent")
