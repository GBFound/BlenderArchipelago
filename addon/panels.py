import bpy
from . import ap_client
from . import deathlink, ids, popup, progress, thresholds, unlocks


class VIEW3D_PT_AP_Similarity(bpy.types.Panel):
    bl_label       = "Similarity"
    bl_idname      = "VIEW3D_PT_AP_Similarity"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Blender AP"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return ap_client.is_connected()

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        percent = bpy.context.scene.current_percent
        goal = progress.goal_percent

        difference = bpy.context.scene.difference
        icon = "ARROW_LEFTRIGHT"
        if difference > 0:
            icon = "SORT_DESC"
        elif difference < 0:
            icon = "SORT_ASC"
        
        if percent != 0:
            row = box.row()
            row.label(text=f"Current Similarity: {percent:.3f}%")
            row.label(text="", icon=icon)
        else:
            box.label(text="Similarity not yet found. Render first.")

        has_more_checks = False
        for i, (threshold, checked) in enumerate(thresholds.data.items()):
            if not checked:
                box.label(text=f"Next Check: {threshold}%")
                has_more_checks = True
                break
        if not has_more_checks:
            i += 1
        box.label(text=f"{i} / {len(thresholds.data)} checks completed.")
        
        box.label(text=f"Goal: {goal:.1f}%")

        box = layout.box()
        box.label(text="Target Image:")
        row = box.row(align=True)
        row.prop_search(context.scene, "ap_target_image", bpy.data, "images", text="")
        row.operator("ap.load_target_image", text="", icon="FILEBROWSER")


class VIEW3D_PT_AP_Unlocked(bpy.types.Panel):
    bl_label       = "Unlocked"
    bl_idname      = "VIEW3D_PT_AP_Unlocked"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Blender AP"
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return ap_client.is_connected()

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        if unlocks.temp_unlock_countdown_timer:
            box.label(text=f"Temporarily unlocked all tools.")
            box.label(text=f"{unlocks.temp_unlock_countdown_timer} seconds left.")
            box = layout.box()

        for item in ids.Item:
            if unlocks.is_trap_or_filler(item):
                break
            if item == ids.Item.PROGRESSIVE_RENDER_WIDTH or item == ids.Item.PROGRESSIVE_RENDER_HEIGHT:
                continue

            is_unlocked = unlocks.get_item_count(item)
            unlock_text = popup.item_to_unlock_text(item)
            row = box.row()
            if is_unlocked or unlocks.unlock_all:
                row.label(text=f"{unlock_text}", icon="UNLOCKED")
            else:
                row.enabled = False
                row.label(text=f"{unlock_text}", icon="LOCKED")


class VIEW3D_PT_AP_Connection(bpy.types.Panel):
    bl_label       = "Connection"
    bl_idname      = "VIEW3D_PT_AP_Connection"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Blender AP"
    bl_order = 2

    def draw(self, context):
        connected = ap_client.is_connected() or ap_client.is_connecting()
        layout = self.layout
        box = layout.box()

        for label, prop in (("Host:", "ap_host"), ("Port:", "ap_port"), ("Slot:", "ap_slot_name"), ("Password:", "ap_password")):
            factor = 0.15
            if prop == "ap_password":
                factor = 0.3
            split = box.split(factor=factor)
            split.label(text=label)
            if connected:
                split.label(text=str(getattr(context.scene, prop)))
            else:
                split.prop(context.scene, prop, text="")

        if ap_client.is_connected():
            box.operator("ap.disconnect", icon="PANEL_CLOSE")
            icon = "GHOST_DISABLED"
            if deathlink.enabled:
                icon = "GHOST_ENABLED"
            box.operator("ap.deathlink_toggle", icon=icon, depress=deathlink.enabled)
        elif ap_client.is_connecting():
            box.operator("ap.connecting", icon="SORTTIME")
        else:
            box.operator("ap.connect", icon="LINKED")


def schedule_redraw_panels():
    bpy.app.timers.register(_redraw_panels)


def _redraw_panels():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def register():
    bpy.types.Scene.ap_target_image = bpy.props.StringProperty(
        name="Target Image",
        description="The target image to compare renders against",
    )

    bpy.types.Scene.ap_deathlink_enabled = bpy.props.BoolProperty(
        name="Deathlink",
        description="When you die, everyone with deathlink dies. The reverse is also true.",
    )

    bpy.types.Scene.ap_host = bpy.props.StringProperty(
        default="archipelago.gg",
        name="Host",
        description="The host server to which to connect.",
    )

    bpy.types.Scene.ap_port = bpy.props.StringProperty(
        default="38281",
        name="Port",
        description="The port to which to connect.",
    )

    bpy.types.Scene.ap_slot_name = bpy.props.StringProperty(
        default="Blenderer",
        name="Slot",
        description="The slot name to use for this game. This is required, and must match the name provided on your YAML file.",
    )
    
    bpy.types.Scene.ap_password = bpy.props.StringProperty(
        default="", subtype="PASSWORD",
        name="Password",
        description="The password to use for this game, if any.",
    )


def unregister():
    del bpy.types.Scene.ap_password
    del bpy.types.Scene.ap_slot_name
    del bpy.types.Scene.ap_port
    del bpy.types.Scene.ap_host
    del bpy.types.Scene.ap_deathlink_enabled
    del bpy.types.Scene.ap_target_image


"""
For debugging.
class VIEW3D_PT_AP_Thresholds(bpy.types.Panel):
    bl_label       = "Thresholds (Debug)"
    bl_idname      = "VIEW3D_PT_AP_Thresholds"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Blender AP"

    @classmethod
    def poll(cls, context):
        return ap_client.is_connected()

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        for threshold, checked in thresholds.data.items():
            if checked:
                box.label(text=f"{threshold}%: CHECKED", icon="UNLOCKED")
            else:
                box.label(text=f"{threshold}%: NOT CHECKED", icon="LOCKED")
"""
