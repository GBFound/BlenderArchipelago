import bpy

goal_percent: int = 50


def initialize_progress(new_goal_percent: int):
    global goal_percent
    goal_percent = new_goal_percent


def register():
    bpy.types.Scene.ap_current_percent = bpy.props.FloatProperty()
    bpy.types.Scene.ap_difference = bpy.props.FloatProperty()


def unregister():
    del bpy.types.Scene.ap_difference
    del bpy.types.Scene.ap_current_percent
