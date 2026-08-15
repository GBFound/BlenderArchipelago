import bpy
import collections

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
        lambda: bpy.ops.ap.popup("INVOKE_DEFAULT", message=message) and None,
    )
    print(f"[Blender AP] {message}")
