import bpy

goal_percent:    int = 50


def initialize_progress(packet: dict):
    global goal_percent
    slot_data = packet.get("slot_data")
    goal_percent = slot_data.get("goal_percent")


def register():
    bpy.types.Scene.current_percent = bpy.props.FloatProperty()


def unregister():
    del bpy.types.Scene.current_percent
