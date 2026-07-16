import bpy
import collections
from . import explosion

_popup_queue = collections.deque()
_show_next_popup = True


def queue_popup(message: str):
    _popup_queue.append(message)

    if _show_next_popup:
        _schedule_popup()


def show_next_popup():
    global _show_next_popup
    _show_next_popup = True
    
    if _popup_queue:
        _schedule_popup()


def _schedule_popup():
    global _show_next_popup
    _show_next_popup = False

    message = _popup_queue.popleft()
    bpy.app.timers.register(
        # Use a timer to defer the call until context is available.
        # Returning None stops the timer from repeating
        lambda: bpy.ops.wm.ap_popup("INVOKE_DEFAULT", message=message) and None,
    )
    print(f"[Blender AP] {message}")



def schedule_undo():
    bpy.app.timers.register(_undo)


def _undo():
    """
    bpy.ops.ed.undo() does not work because uhh.
    Ideally this would only undo a few steps, but the undo stack size isn't readable until Blender 5.3.
    Currently undos to the bottom of the undo history
    """
    from . import ap_client
    ap_client.suppress_deathlink = True

    try:
        bpy.ops.ed.undo_history(item=0)
    except Exception as e:
        print(f"[Blender AP] Undo failed: {e}")
        
    ap_client.suppress_deathlink = False
    explosion.spawn_animated_ref_image()
