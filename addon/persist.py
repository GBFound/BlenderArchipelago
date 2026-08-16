from . import ids

item_counts:        dict[ids.Item, int] = {}
ap_data_package:    dict                = {}
current_percent:    int                 = 0
difference:         int                 = 0
ap_last_item_index: int                 = 0
ap_target_image:    str                 = ""
ap_host:            str                 = ""
ap_port:            str                 = ""
ap_slot_name:       str                 = ""
ap_password:        str                 = ""

SIMPLE_SCENE_FIELDS = [
    "current_percent",
    "difference",
    "ap_last_item_index",
    "ap_target_image",
    "ap_host",
    "ap_port",
    "ap_slot_name",
    "ap_password",
]
