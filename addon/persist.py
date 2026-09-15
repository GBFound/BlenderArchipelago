"""
Blender's bpy.context.scene properties are useful for storing data across files 
save and loads. However, Blender's undo system works by restoring the entire
scene from a memory snapshot, which also reverts bpy.context.scene properties. 
This includes properties used to track game progress, which should not revert.

Values stored here live outside Blender's undo system, so they survive 
undo/redo. Call sites that write to both bpy.context.scene and a value here 
should treat persist as the source of truth, and any undo/redo handler should 
resync bpy.context.scene from these values afterward.
"""

from . import ids

# Connection settings
ap_host: str = ""
ap_port: str = ""
ap_slot_name: str = ""
ap_password: str = ""

# Target image
ap_target_image: str = ""
ap_target_image_filepath: str = ""

# Progress tracking
ap_current_percent: int = 0
ap_difference: int = 0
ap_has_reached_goal: bool = False

# Item tracking
ap_item_counts: dict[ids.Item, int] = {}
ap_last_item_index: int = 0
ap_materials_unlocked_by: str = ""

# Options
ap_progressive_render_width_max: int = 0
ap_progressive_render_height_max: int = 0

# ap_item_counts need custom (de)serialization and is handled separately
SIMPLE_SCENE_FIELDS = [
    "ap_host",
    "ap_port",
    "ap_slot_name",
    "ap_password",

    "ap_target_image",
    "ap_target_image_filepath",

    "ap_current_percent",
    "ap_difference",
    "ap_has_reached_goal",

    "ap_progressive_render_width_max",
    "ap_progressive_render_height_max",

    "ap_last_item_index",
    "ap_materials_unlocked_by",
]
