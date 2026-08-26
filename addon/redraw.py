import bpy

def schedule_redraw_panels():
    bpy.app.timers.register(_redraw_panels)


def _redraw_panels():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
