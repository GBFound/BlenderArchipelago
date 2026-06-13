BASE_ID = 7897897890

ITEMS = [
    "edit_mode",
    "sculpt_mode",
    "vertex_paint_mode",
    "weight_paint_mode",
    "texture_paint_mode",
]

LOCATIONS = [
    "similarity_check_0",
    "similarity_check_1",
    "similarity_check_2",
    "similarity_check_3",
    "similarity_check_4",
]

ITEM_ID_TO_NAME     = {BASE_ID + i: name for i, name in enumerate(ITEMS)}
ITEM_NAME_TO_ID     = {name: BASE_ID + i for i, name in enumerate(ITEMS)}
LOCATION_NAME_TO_ID = {name: BASE_ID + i for i, name in enumerate(LOCATIONS)}
LOCATION_ID_TO_NAME = {BASE_ID + i: name for i, name in enumerate(LOCATIONS)}
