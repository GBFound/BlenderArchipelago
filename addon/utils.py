import bpy

def popup(message: str):
    bpy.app.timers.register(
        # Use a timer to defer the call until context is available.
        # Returning None stops the timer from repeating
        lambda: bpy.ops.wm.ap_popup("INVOKE_DEFAULT", message=message) and None,
    )
    print(f"[Blender AP] {message}")


def undo():
    bpy.app.timers.register(_undo)


def _undo():
    """
    bpy.ops.ed.undo() does not work because uhh.
    Ideally this would only undo a few steps, but the undo stack size isn't readable until Blender 5.3.
    Currently undos to the bottom of the undo history
    """
    from . import ap_client
    ap_client.suppress_deathlink = True
    bpy.ops.ed.undo_history(item=0)
    ap_client.suppress_deathlink = False
