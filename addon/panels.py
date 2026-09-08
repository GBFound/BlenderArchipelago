import bpy
from . import client, deathlink, ids, popup, progress, thresholds, unlocks


class AP_PT_Similarity(bpy.types.Panel):
    bl_label       = "Similarity"
    bl_idname      = "AP_PT_Similarity"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Archipelago"
    bl_order       = 0

    @classmethod
    def poll(cls, context):
        return client.is_connected()

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        percent = bpy.context.scene.ap_current_percent
        goal = progress.goal_percent

        ap_difference = bpy.context.scene.ap_difference
        icon = "ARROW_LEFTRIGHT"
        if ap_difference > 0:
            icon = "SORT_DESC"
        elif ap_difference < 0:
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

        completed_text = ""
        if bpy.context.scene.ap_has_reached_goal:
            completed_text = " - Completed!"
        box.label(text=f"Goal: {goal:.1f}%{completed_text}")


class AP_PT_Target(bpy.types.Panel):
    bl_label       = "Target Image"
    bl_idname      = "AP_PT_Target"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Archipelago"
    bl_order       = 1

    @classmethod
    def poll(cls, context):
        return client.is_connected()

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.prop_search(context.scene, "ap_target_image", bpy.data, "images", text="")
        row.operator("ap.load_target_image", text="", icon="FILEBROWSER")


class AP_PT_Unlocked(bpy.types.Panel):
    bl_label       = "Unlocked"
    bl_idname      = "AP_PT_Unlocked"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Archipelago"
    bl_order       = 2

    @classmethod
    def poll(cls, context):
        return client.is_connected()

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
            if unlocks.is_progressive_render_border(item):
                continue

            is_unlocked = unlocks.get_item_count(item)
            unlock_text = popup.item_to_unlock_text(item)
            row = box.row()
            if is_unlocked:
                row.label(text=f"{unlock_text}", icon="UNLOCKED")
            elif unlocks.unlock_all:
                row.label(text=f"{unlock_text}", icon="TIME")
            else:
                row.enabled = False
                row.label(text=f"{unlock_text}", icon="LOCKED")


# class AP_PT_Messages(bpy.types.Panel):
#     bl_label       = "Messages"
#     bl_idname      = "AP_PT_Messages"
#     bl_space_type  = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category    = "Archipelago"
#     bl_order       = 3

#     @classmethod
#     def poll(cls, context):
#         return client.is_connected()

#     def draw(self, context):
#         layout = self.layout
#         layout.template_list(
#             listtype_name="AP_UL_Messages",
#             list_id="",
#             dataptr=context.scene, propname="ap_messages",
#             active_dataptr=context.scene, active_propname="ap_messages_index",
#         )


class AP_PT_Connection(bpy.types.Panel):
    bl_label       = "Connection"
    bl_idname      = "AP_PT_Connection"
    bl_space_type  = "VIEW_3D"
    bl_region_type = "UI"
    bl_category    = "Archipelago"
    bl_order       = 4

    def draw(self, context):
        connected = client.is_connected() or client.is_connecting()
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

        if client.is_connected():
            icon = "GHOST_DISABLED"
            if deathlink.enabled:
                icon = "GHOST_ENABLED"
            box.operator("ap.deathlink_toggle", icon=icon, depress=deathlink.enabled)
            box.operator("ap.disconnect", icon="PANEL_CLOSE")
        elif client.is_connecting():
            box.operator("ap.connecting", icon="SORTTIME")
        else:
            box.operator("ap.connect", icon="LINKED")
