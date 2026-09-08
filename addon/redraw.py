import bpy


def panels():
    bpy.app.timers.register(_panels)


def _panels():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
