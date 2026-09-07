from . import ids

ap_item_counts           : dict[ids.Item, int] = {}
ap_data_package          : dict                = {}
ap_current_percent       : int                 = 0
ap_difference            : int                 = 0
ap_last_item_index       : int                 = 0
ap_target_image          : str                 = ""
ap_host                  : str                 = ""
ap_port                  : str                 = ""
ap_slot_name             : str                 = ""
ap_password              : str                 = ""
ap_materials_unlocked_by : str                 = ""

SIMPLE_SCENE_FIELDS = [
    "ap_current_percent",
    "ap_difference",
    "ap_last_item_index",
    "ap_target_image",
    "ap_host",
    "ap_port",
    "ap_slot_name",
    "ap_password",
    "ap_materials_unlocked_by",
]
