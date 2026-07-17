import bpy
from . import ids, panels, utils

data = {item: 0 for item in ids.Item if item < ids.Item.POPUP}
resyncing = False

def unlock_item(item: ids.Item):
    if _is_trap_or_filler(item):
        if not resyncing:
            _activate_filler_and_traps(item)
        return
    
    data[item] += 1
    panels.schedule_redraw_panels()


def clear_unlocks():
    for item in data:
        data[item] = 0


def _is_trap_or_filler(item: ids.Item) -> bool:
    return item >= ids.Item.POPUP


def _activate_filler_and_traps(item: ids.Item):
    if item == ids.Item.POPUP:
        utils.queue_popup("your model look like poop from a butt 💔💔💔")
    elif item == ids.Item.UNDO or item == ids.Item.DESPAIR:  # TODO Currently placeholder for DESPAIR
            utils.schedule_undo()
            utils.queue_popup("Undo trap.")


def register():
    bpy.types.Scene.ap_last_item_index = bpy.props.IntProperty()


def unregister():
    del bpy.types.Scene.ap_last_item_index
