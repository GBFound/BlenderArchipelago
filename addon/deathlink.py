import bpy
import random
import threading
from . import explosion

_enabled: bool = False
_enabled_lock: threading.Lock = threading.Lock()

# Suppresses deathlink when an undo is caused by an undo trap
suppressed: bool = False


def choose_message(do: str) -> str:
    message = f" hit {do}."
    message_choice = random.randint(0, 2)
    if message_choice == 2:
        message = "'s model look like poop from a butt 💔💔💔"
    return message


def toggle():
    global _enabled
    with _enabled_lock:
        _enabled = not _enabled


def set_enabled(value: bool):
    global _enabled
    with _enabled_lock:
        _enabled = value


def get_enabled() -> bool:
    with _enabled_lock:
        return _enabled


def undo():
    bpy.app.timers.register(_undo)


def _undo():
    """
    Undos to the bottom of the undo history.
    Fun facts:
    1. bpy.ops.ed.undo() does not work because uhh.
    2. Undo stack size isn't readable until Blender 5.3.
    """
    global suppressed
    suppressed = True

    try:
        bpy.ops.ed.undo_history(item=0)
    except Exception as e:
        print(f"[Archipelago] Undo failed: {e}")

    suppressed = False
    explosion.spawn_animated_ref_image()
