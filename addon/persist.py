from . import ids

# Connection settings
ap_host                  : str                 = ""
ap_port                  : str                 = ""
ap_slot_name             : str                 = ""
ap_password              : str                 = ""

# Target image
ap_target_image          : str                 = ""
ap_target_image_filepath : str                 = ""

# Progress tracking
ap_current_percent       : int                 = 0
ap_difference            : int                 = 0

# Item tracking
ap_item_counts           : dict[ids.Item, int] = {}
ap_last_item_index       : int                 = 0
ap_materials_unlocked_by : str                 = ""

# Data package
ap_data_package          : dict                = {}


# ap_item_counts and ap_data_package need custom (de)serialization and are handled separately
SIMPLE_SCENE_FIELDS = [
    "ap_host",
    "ap_port",
    "ap_slot_name",
    "ap_password",

    "ap_target_image",
    "ap_target_image_filepath",

    "ap_current_percent",
    "ap_difference",

    "ap_last_item_index",
    "ap_materials_unlocked_by",
]
