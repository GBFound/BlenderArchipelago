import bpy
import json
from . import deathlink, ids, panels, popup

resyncing = False


class ItemCounts(bpy.types.PropertyGroup):
    pass

annotations = {}
for item in ids.Item:
    if item >= ids.Item.POPUP:
        break
    annotations[item.name] = bpy.props.IntProperty(name=item.name, default=0)

ItemCounts.__annotations__ = annotations


_TEXT_NAME = "ap_item_counts.json"

def _get_counts_text():
    text = bpy.data.texts.get(_TEXT_NAME)
    if text is None:
        text = bpy.data.texts.new(_TEXT_NAME)
        initial_counts = {}
        for item in ids.Item:
            if item >= ids.Item.POPUP:
                break
            initial_counts[item.name] = 0
        initial_json = json.dumps(initial_counts)
        text.write(initial_json)
    return text

def get_item_count(item: ids.Item) -> int:
    data = json.loads(_get_counts_text().as_string())
    return data.get(item.name, 0)

def set_item_count(item: ids.Item, value: int):
    text = _get_counts_text()
    data = json.loads(text.as_string())
    data[item.name] = value
    text.clear()
    text.write(json.dumps(data))


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
