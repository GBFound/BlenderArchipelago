import bpy
import random
from . import explosion

enabled:    bool = False

# Suppresses deathlink when an undo is caused by an undo trap
suppressed: bool = False


def choose_message(do: str) -> str:
    message = f" hit {do}."
    message_choice = random.randint(0, 2)
    if message_choice == 2:
        message = "'s model look like poop from a butt 💔💔💔"
    return message


def schedule_undo():
    bpy.app.timers.register(_undo)


def _undo():
    """
    bpy.ops.ed.undo() does not work because uhh.
    Ideally this would only undo a few steps, but the undo stack size isn't readable until Blender 5.3.
    Currently undos to the bottom of the undo history
    """
    global suppressed
    suppressed = True

    try:
        bpy.ops.ed.undo_history(item=0)
    except Exception as e:
        print(f"[Blender AP] Undo failed: {e}")
        
    suppressed = False
    explosion.spawn_animated_ref_image()
