import bpy
from . import deathlink, ids, panels, persist, popup

resyncing = False


class ItemCounts(bpy.types.PropertyGroup):
    pass

annotations = {}
for item in ids.Item:
    if item >= ids.Item.POPUP:
        break
    annotations[item.name] = bpy.props.IntProperty(name=item.name, default=0)
    persist.item_counts[item] = 0

ItemCounts.__annotations__ = annotations


def get_item_count(item: ids.Item) -> int:
    counts = bpy.context.scene.item_counts
    return getattr(counts, item.name)


def set_item_count(item: ids.Item, value: int):
    counts = bpy.context.scene.item_counts
    setattr(counts, item.name, value)
    persist.item_counts[item] = value


def unlock_item(item: ids.Item):
    if is_trap_or_filler(item):
        if not resyncing:
            _activate_filler_and_traps(item)
        return

    set_item_count(item, get_item_count(item) + 1)
    panels.schedule_redraw_panels()


def clear_unlocks():
    for item in ids.Item:
        if is_trap_or_filler(item):
            break
        set_item_count(item, 0)


def is_trap_or_filler(item: ids.Item) -> bool:
    return item >= ids.Item.POPUP


def schedule_last_index(index: int):
    bpy.app.timers.register(lambda: _set_last_index(index))


def _set_last_index(index: int):
    bpy.context.scene.ap_last_item_index = index
    persist.ap_last_item_index = index


def _activate_filler_and_traps(item: ids.Item):
    if item == ids.Item.POPUP:
        popup.enqueue("your model look like poop from a butt 💔💔💔")
    elif item == ids.Item.UNDO or item == ids.Item.DESPAIR:  # TODO Currently placeholder for DESPAIR
        deathlink.schedule_undo()
        popup.enqueue("Undo trap.")


def register():
    bpy.types.Scene.item_counts = bpy.props.PointerProperty(type=ItemCounts)
    bpy.types.Scene.ap_last_item_index = bpy.props.IntProperty()


def unregister():
    del bpy.types.Scene.ap_last_item_index
    del bpy.types.Scene.item_counts
