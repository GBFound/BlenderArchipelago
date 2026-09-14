import bpy
from . import popup, redraw

_countdown_seconds = 0
_duration_seconds = 0


def is_unlock_all() -> bool:
    return _countdown_seconds > 0


def set_duration(seconds: int):
    global _duration_seconds
    _duration_seconds = seconds


def get_countdown() -> int:
    return _countdown_seconds


def unlock_all(seconds: int = None):
    global _countdown_seconds

    if seconds is None:
        seconds = _duration_seconds

    _countdown_seconds += seconds
    if _countdown_seconds == seconds:
        bpy.app.timers.register(_unlock_all_countdown_timer)
    popup.enqueue(f"Temporarily unlocked all tools for +{seconds} seconds.")


def _unlock_all_countdown_timer() -> int:
    global _countdown_seconds

    redraw.panels()
    if popup.can_show_next:  # Pause countdown when there is a popup to be nice
        _countdown_seconds -= 1
    if not _countdown_seconds:
        redraw.panels()
        popup.enqueue("Temporary unlocks have ended.")
        return None

    return 1
