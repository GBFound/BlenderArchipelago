import bpy
import collections
from . import ids

_can_show_next = True
_popups = collections.deque()


def enqueue(message: str):
    _popups.append(message)

    if _can_show_next:
        _schedule()


def show_next():
    global _can_show_next
    _can_show_next = True
    
    if _popups:
        _schedule()


def can_show_next() -> bool:
    return _can_show_next


def item_to_unlock_text(item: ids.Item) -> str:
    return item.name.replace("_", " ").title()


def _schedule():
    global _can_show_next
    _can_show_next = False

    message = _popups.popleft()
    bpy.app.timers.register(
        # Use a timer to defer the call until context is available.
        # Returning None stops the timer from repeating
        lambda: bpy.ops.ap.popup("INVOKE_DEFAULT", message=message) and None,
    )
    print(f"[Archipelago] {message}")
