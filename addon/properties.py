import bpy

from . import messages, unlocks


_properties = {
    # Connection settings
    "ap_host": bpy.props.StringProperty(
        default="archipelago.gg",
        name="Host",
        description="The host server to which to connect.",
    ),
    "ap_port": bpy.props.StringProperty(
        default="38281",
        name="Port",
        description="The port to which to connect.",
    ),
    "ap_slot_name": bpy.props.StringProperty(
        default="Blenderer",
        name="Slot",
        description="The slot name to use for this game. This is required, and must match the name provided on your YAML file.",
    ),
    "ap_password": bpy.props.StringProperty(
        default="", subtype="PASSWORD",
        name="Password",
        description="The password to use for this game, if any.",
    ),
    "ap_deathlink_enabled": bpy.props.BoolProperty(
        name="Deathlink",
        description="When you die, everyone with deathlink dies. The reverse is also true.",
    ),

    # Target image
    "ap_target_image": bpy.props.StringProperty(
        name="Target Image",
        description="The target image to compare renders against",
    ),
    "ap_target_image_filepath": bpy.props.StringProperty(),

    # Progress tracking
    "ap_current_percent": bpy.props.FloatProperty(),
    "ap_difference": bpy.props.FloatProperty(),

    # Item tracking
    "ap_item_counts": bpy.props.PointerProperty(type=unlocks.ItemCounts),
    "ap_last_item_index": bpy.props.IntProperty(),
    "ap_materials_unlocked_by": bpy.props.StringProperty(),

    # Messages
    "ap_messages": bpy.props.CollectionProperty(type=messages.Message),
    "ap_messages_index": bpy.props.IntProperty(),
}


def register():
    for name, property in _properties.items():
        setattr(bpy.types.Scene, name, property)


def unregister():
    for name in _properties:
        delattr(bpy.types.Scene, name)
