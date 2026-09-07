import bpy
import random
from . import deathlink, despair, ids, persist, popup, redraw

progressive_render_width_max = 0
progressive_render_height_max = 0
temp_unlock_duration_seconds = 60
temp_unlock_countdown_timer = 0
unlock_all = False
resyncing = False


_MATERIALS_DEPENDENTS = (
    ids.Item.VERTEX_PAINT_MODE,
    ids.Item.TEXTURE_PAINT_MODE,
    ids.Item.GREASE_PENCIL_MODES,
)


class ItemCounts(bpy.types.PropertyGroup):
    pass

annotations = {}
for item in ids.Item:
    if item == ids.Item.PROGRESSIVE_RENDER_WIDTH or item == ids.Item.PROGRESSIVE_RENDER_HEIGHT:
        annotations[item.name] = bpy.props.IntProperty(name=item.name, default=0)
        persist.item_counts[item] = 0
    annotations[item.name] = bpy.props.IntProperty(name=item.name, default=1)
    persist.item_counts[item] = 1

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

    if is_progressive_render_border(item):
        redraw.render_border()
    redraw.panels()


def clear_unlocks():
    for item in ids.Item:
        set_item_count(item, 0)

    bpy.context.scene.materials_unlocked_by = ""


def is_progressive_render_border(item: ids.Item) -> bool:
    return item == ids.Item.PROGRESSIVE_RENDER_WIDTH or item == ids.Item.PROGRESSIVE_RENDER_HEIGHT


def is_trap_or_filler(item: ids.Item) -> bool:
    return item >= ids.Item.POPUP


def set_last_index(index: int):
    bpy.app.timers.register(lambda: _set_last_index(index))


def initialize_unlocks(new_width_max: int, new_height_max: int, new_temp_unlock_duration_seconds: int):
    global progressive_render_width_max, progressive_render_height_max, temp_unlock_duration_seconds

    progressive_render_width_max = new_width_max
    progressive_render_height_max = new_height_max
    temp_unlock_duration_seconds = new_temp_unlock_duration_seconds


def temp_unlock_all_tools(duration=None):
    global temp_unlock_countdown_timer, unlock_all

    if duration == None:
        duration = temp_unlock_duration_seconds

    unlock_all = True
    temp_unlock_countdown_timer += duration
    if temp_unlock_countdown_timer == duration:
        bpy.app.timers.register(_temp_unlock_countdown_timer)
    popup.enqueue(f"Temporarily unlocked all tools for +{duration} seconds.")


def _temp_unlock_countdown_timer() -> int:
    global temp_unlock_countdown_timer

    redraw.panels()
    if popup.can_show_next:  # Pause timer when there is a popup to be nice
        temp_unlock_countdown_timer -= 1
    if not temp_unlock_countdown_timer:
        _relock_all_tools()
        return None
    
    return 1


def _relock_all_tools():
    global unlock_all
    unlock_all = False
    redraw.panels()
    popup.enqueue("Temporary unlocks have ended.")


def _set_last_index(index: int):
    bpy.context.scene.ap_last_item_index = index
    persist.ap_last_item_index = index


def _activate_filler_and_traps(item: ids.Item):
    if item == ids.Item.POPUP:
        messages = [
            "You're doing great!",
            "your doing great",
            "i bet this model looking so good rn",
            "your model look like poop from a butt 💔💔💔",
        ]
        message = random.choice(messages)
        popup.enqueue(message)
    elif item == ids.Item.FULL_ARSENAL:
        temp_unlock_all_tools()
    elif item == ids.Item.UNDO:
        deathlink.undo()
        popup.enqueue("Undo trap.")
    elif item == ids.Item.DESPAIR:
        despair.despair()


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
    elif item == ids.Item.MATERIALS and not materials_unlocked_by:
        bpy.context.scene.materials_unlocked_by = item.name
        persist.materials_unlocked_by = item.name
    
    return item


def _popup_unless_resyncing(message: str):
    if not resyncing:
        popup.enqueue(message)


def register():
    bpy.types.Scene.item_counts = bpy.props.PointerProperty(type=ItemCounts)
    bpy.types.Scene.ap_last_item_index = bpy.props.IntProperty()
    bpy.types.Scene.materials_unlocked_by = bpy.props.StringProperty()


def unregister():
    del bpy.types.Scene.materials_unlocked_by
    del bpy.types.Scene.ap_last_item_index
    del bpy.types.Scene.item_counts
