import bpy
from . import ap_client
from . import progress, unlocks, thresholds, ids


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
        percent = progress.current_percent
        goal = progress.goal_percent
        if percent is not None:
            box.label(text=f"Current Similarity: {percent:.3f}%")
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
        row.operator("wm.ap_load_target_image", text="", icon="FILEBROWSER")


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
        for item, is_unlocked in unlocks.data.items():
            if item == ids.Item.PROGRESSIVE_RENDER_WIDTH or item == ids.Item.PROGRESSIVE_RENDER_HEIGHT:
                continue
            unlock_text = item.name.replace("_", " ").title()
            if is_unlocked:
                box.label(text=f"{unlock_text}: UNLOCKED", icon="UNLOCKED")
            else:
                box.label(text=f"{unlock_text}: LOCKED", icon="LOCKED")


# class VIEW3D_PT_AP_Thresholds(bpy.types.Panel):
#     bl_label       = "Thresholds (Debug)"
#     bl_idname      = "VIEW3D_PT_AP_Thresholds"
#     bl_space_type  = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category    = "Blender AP"

#     @classmethod
#     def poll(cls, context):
#         return ap_client.is_connected()

#     def draw(self, context):
#         layout = self.layout
#         box = layout.box()

#         for threshold, checked in thresholds.data.items():
#             if checked:
#                 box.label(text=f"{threshold}%: CHECKED", icon="UNLOCKED")
#             else:
#                 box.label(text=f"{threshold}%: NOT CHECKED", icon="LOCKED")


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
            box.operator("wm.ap_disconnect", icon="PANEL_CLOSE")
        elif ap_client.is_connecting():
            box.operator("wm.ap_connecting", icon="SORTTIME")
        else:
            box.operator("wm.ap_connect", icon="LINKED")


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
    bpy.types.Scene.ap_host      = bpy.props.StringProperty(default="archipelago.gg")
    bpy.types.Scene.ap_port      = bpy.props.StringProperty(default="38281")
    bpy.types.Scene.ap_slot_name = bpy.props.StringProperty(default="Player")
    bpy.types.Scene.ap_password  = bpy.props.StringProperty(default="", subtype="PASSWORD")


def unregister():
    del bpy.types.Scene.ap_target_image
    del bpy.types.Scene.ap_host
    del bpy.types.Scene.ap_port
    del bpy.types.Scene.ap_slot_name
    del bpy.types.Scene.ap_password
