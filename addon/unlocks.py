import bpy
from . import ids, panels, utils

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
    panels.schedule_redraw_panels()


def clear_unlocks():
    for item in data:
        data[item] = False


def _is_trap_or_filler(item: ids.Item) -> bool:
    return item >= ids.Item.POP_UP


def _activate_filler_and_traps(item: ids.Item):
    match item:
        case ids.Item.POP_UP:
            utils.queue_popup("your model look like poop from a butt 💔💔💔")
        case ids.Item.UNDO:
            utils.schedule_undo()
            utils.queue_popup("Undo trap.")


def register():
    bpy.types.Scene.ap_last_item_index = bpy.props.IntProperty()


def unregister():
    del bpy.types.Scene.ap_last_item_index
