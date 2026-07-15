import bpy
from . import explosion, ids, panels, utils

data = {item: False for item in ids.Item if item < ids.Item.POP_UP}
resyncing = False

def unlock_item(item: ids.Item):
    if data.get(item):
        return
    
    if _is_trap_or_filler(item):
        if not resyncing:
            _activate_filler_and_traps(item)
        return
    
    data[item] = True
    panels.redraw_panels()

    if not resyncing:
        unlock_text = item.name.replace("_", " ").title()
        utils.popup(f"{unlock_text} has been unlocked!")


def clear_unlocks():
    print(f"[Blender AP] Clearing unlocks.")
    for item in data:
        data[item] = False


def _is_trap_or_filler(item: ids.Item) -> bool:
    return item >= ids.Item.POP_UP


def _activate_filler_and_traps(item: ids.Item):
    match item:
        case ids.Item.POP_UP:
            utils.popup("your model look like poop from a butt 💔💔💔")
        case ids.Item.UNDO:
            utils.undo()
            bpy.app.timers.register(explosion.spawn_animated_ref_image)
            utils.popup("Undo trap.")


def register():
    bpy.types.Scene.ap_last_item_index = bpy.props.IntProperty()


def unregister():
    del bpy.types.Scene.ap_last_item_index
