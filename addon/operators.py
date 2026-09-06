import bpy
from . import ap_client, deathlink, handlers, persist, popup


class AP_OT_Popup(bpy.types.Operator):
    """Pop-Up"""
    bl_label  = "Archipelago"
    bl_idname = "ap.popup"

    message: bpy.props.StringProperty(default="")

    def execute(self, context):
        return {"FINISHED"}
    
    def cancel(self, context):
        popup.show_next()

    def invoke(self, context, event):
        width = len(self.message) * 6
        return context.window_manager.invoke_popup(self, width=width)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.bl_label, icon="INFO")
        layout.label(text=self.message)


class AP_OT_LoadTargetImage(bpy.types.Operator):
    """Load Target Image"""
    bl_label  = "Load Target Image"
    bl_idname = "ap.load_target_image"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_image: bpy.props.BoolProperty(default=True, options={"HIDDEN"})
    filter_folder: bpy.props.BoolProperty(default=True, options={"HIDDEN"})

    def execute(self, context):
        camera = context.scene.camera
        if not camera:
            popup.enqueue("Set active camera before loading the target image.")
            return {"FINISHED"}

        image = bpy.data.images.load(self.filepath)
        context.scene.ap_target_image = image.name
        persist.ap_target_image = image.name
        context.scene.render.resolution_x = image.size[0]
        context.scene.render.resolution_y = image.size[1]
        handlers.use_render_border(context.scene)

        bg = camera.data.background_images.new()
        bg.image = image
        camera.data.show_background_images = True
        camera.data.background_images[0].alpha = 1
        
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class AP_OT_Connect(bpy.types.Operator):
    """Connect to Archipelago"""
    bl_label  = "Connect to Archipelago"
    bl_idname = "ap.connect"

    def execute(self, context):
        scene = context.scene
        ap_client.connect(
            host=scene.ap_host,
            port=scene.ap_port,
            slot_name=scene.ap_slot_name,
            password=scene.ap_password,
        )
        persist.ap_host = scene.ap_host
        persist.ap_port = scene.ap_port
        persist.ap_slot_name = scene.ap_slot_name
        persist.ap_password = scene.ap_password
        return {"FINISHED"}


class AP_OT_Disconnect(bpy.types.Operator):
    """Disconnect from Archipelago"""
    bl_label  = "Disconnect from Archipelago"
    bl_idname = "ap.disconnect"

    def execute(self, context):
        ap_client.disconnect()
        return {"FINISHED"}


class AP_OT_Connecting(bpy.types.Operator):
    """King Crimson - Matte Kudasai"""
    bl_label  = "Please wait..."  # Covers connecting and disconnecting
    bl_idname = "ap.connecting"

    def execute(self, context):
        return {"FINISHED"}


class AP_OT_Deathlink_Toggle(bpy.types.Operator):
    """Deathlink Toggle"""
    bl_idname = "ap.deathlink_toggle"
    bl_label = "Deathlink"

    def execute(self, context):
        deathlink.enabled = not deathlink.enabled
        ap_client.send_deathlink_tag_update()
        return {"FINISHED"}


"""
class AP_OT_Debug(bpy.types.Operator):
    bl_idname = "ap.debug"
    bl_label = "Awesome Debug"
    bl_options = {"UNDO"}

    def execute(self, context):
        return {"FINISHED"}
"""


"""
Does not work unless invoked by the user.
Was to be used for less obtrusive popups.
class AP_OT_Report(bpy.types.Operator):
    bl_label  = "Archipelago"
    bl_idname = "ap.report"

    message: bpy.props.StringProperty()

    def execute(self, context):
        self.report({"INFO"}, self.message)
        return {"FINISHED"}
"""
