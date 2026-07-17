from enum import IntEnum, auto

BASE_ID = 7897897890

class Item(IntEnum):
    def _generate_next_value_(name, start, count, last_values):
        return count  # 0, 1, 2... instead of the default 1, 2, 3...

    PROGRESSIVE_RENDER_WIDTH  = auto()  # 0
    PROGRESSIVE_RENDER_HEIGHT = auto()  # 1
    EDIT_MODE                 = auto()  # 2
    SCULPT_MODE               = auto()  # ...
    VERTEX_PAINT_MODE         = auto()
    WEIGHT_PAINT_MODE         = auto()
    TEXTURE_PAINT_MODE        = auto()
    GREASE_PENCIL_MODES       = auto()
    MATERIALS                 = auto()
    MODIFIERS                 = auto()
    WORLD_SHADERS             = auto()

    # Put fillers and traps after POPUP
    POPUP                     = auto()
    UNDO                      = auto()
    DESPAIR                   = auto()

ID_TO_ITEM : dict[int, Item] = {BASE_ID + item.value: item for item in Item}
