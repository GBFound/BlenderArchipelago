import bpy
from . import deathlink, ids, panels, persist, popup

resyncing = False
progressive_render_width_max = 0
progressive_render_height_max = 0

_MATERIALS_DEPENDENTS = (
    ids.Item.VERTEX_PAINT_MODE,
    ids.Item.TEXTURE_PAINT_MODE,
    ids.Item.GREASE_PENCIL_MODES,
)


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

    item = _resolve_materials_redirect(item)
    set_item_count(item, get_item_count(item) + 1)
    panels.schedule_redraw_panels()


def clear_unlocks():
    for item in ids.Item:
        if is_trap_or_filler(item):
            break
        set_item_count(item, 0)

    bpy.context.scene.materials_unlocked_by = ""
    

def is_trap_or_filler(item: ids.Item) -> bool:
    return item >= ids.Item.POPUP


def schedule_last_index(index: int):
    bpy.app.timers.register(lambda: _set_last_index(index))


def initialize_progressive_render_borders(new_width_max: int, new_height_max: int):
    global progressive_render_width_max, progressive_render_height_max
    progressive_render_width_max = new_width_max
    progressive_render_height_max = new_height_max
    persist.progressive_render_width = new_width_max
    persist.progressive_render_height = new_height_max


def _set_last_index(index: int):
    bpy.context.scene.ap_last_item_index = index
    persist.ap_last_item_index = index


def _activate_filler_and_traps(item: ids.Item):
    if item == ids.Item.POPUP:
        popup.enqueue("your model look like poop from a butt 💔💔💔")
    elif item == ids.Item.UNDO or item == ids.Item.DESPAIR:  # TODO Currently placeholder for DESPAIR
        deathlink.schedule_undo()
        popup.enqueue("Undo trap.")


def _resolve_materials_redirect(item: ids.Item) -> ids.Item:
    materials_unlocked_by = bpy.context.scene.materials_unlocked_by
    if item in _MATERIALS_DEPENDENTS and not materials_unlocked_by:
        bpy.context.scene.materials_unlocked_by = item.name
        persist.materials_unlocked_by = item.name
        item = ids.Item.MATERIALS
        _popup_unless_resyncing("Does not have Materials. Unlocked Materials instead.")
    elif item == ids.Item.MATERIALS and materials_unlocked_by and not get_item_count(ids.Item[materials_unlocked_by]):
        item = ids.Item[materials_unlocked_by]
        unlock_text = popup.item_to_unlock_text(item)
        _popup_unless_resyncing(f"Already have Materials. Unlocked {unlock_text} instead.")
    
    return item


def _popup_unless_resyncing(message: str):
    if not resyncing:
        popup.enqueue(message)


def register():
    bpy.types.Scene.item_counts = bpy.props.PointerProperty(type=ItemCounts)
    bpy.types.Scene.ap_last_item_index = bpy.props.IntProperty()
    bpy.types.Scene.materials_unlocked_by = bpy.props.StringProperty()


def unregister():
    del bpy.types.Scene.ap_last_item_index
    del bpy.types.Scene.item_counts
