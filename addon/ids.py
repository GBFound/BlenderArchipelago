from enum import IntEnum

BASE_ID = 7897897890

class Item(IntEnum):
    EDIT_MODE          = 0
    SCULPT_MODE        = 1
    VERTEX_PAINT_MODE  = 2
    WEIGHT_PAINT_MODE  = 3
    TEXTURE_PAINT_MODE = 4
    MATERIALS          = 5

ITEMS     = tuple(item.name for item in Item)
LOCATIONS = tuple(f"similarity_check_{i}" for i in range(len(ITEMS)))

ID_TO_ITEM     : dict[int, Item] = {BASE_ID + item.value: item for item in Item}
ITEM_TO_ID     : dict[Item, int] = {item: BASE_ID + item.value for item in Item}
LOCATION_TO_ID : dict[str, int]  = {location: BASE_ID + i for i, location in enumerate(LOCATIONS)}
ID_TO_LOCATION : dict[int, str]  = {BASE_ID + i: location for i, location in enumerate(LOCATIONS)}