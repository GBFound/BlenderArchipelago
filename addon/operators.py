import bpy
from . import ap_client


class WM_OT_AP_Popup(bpy.types.Operator):
    bl_label   = "AP Popup"
    bl_idname  = "wm.ap_popup"

    message: bpy.props.StringProperty(default="")

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=280)

    def draw(self, context):
        layout = self.layout
        layout.label(text=self.bl_label, icon="INFO")
        layout.label(text=self.message)


class WM_OT_AP_LoadTargetImage(bpy.types.Operator):
    bl_label   = "AP Load Target Image"
    bl_idname  = "wm.ap_load_target_image"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_image: bpy.props.BoolProperty(default=True, options={"HIDDEN"})
    filter_folder: bpy.props.BoolProperty(default=True, options={"HIDDEN"})

    def execute(self, context):
        image = bpy.data.images.load(self.filepath)
        context.scene.ap_target_image = image.name
        bpy.context.scene.render.resolution_x = image.size[0]
        bpy.context.scene.render.resolution_y = image.size[1]
        
        camera = bpy.context.scene.camera
        bg = camera.data.background_images.new()
        bg.image = image
        camera.data.show_background_images = True
        
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class WM_OT_AP_Connect(bpy.types.Operator):
    bl_label  = "Connect to Archipelago"
    bl_idname = "wm.ap_connect"

    def execute(self, context):
        scene = context.scene
        ap_client.connect(
            host=scene.ap_host,
            port=scene.ap_port,
            slot_name=scene.ap_slot_name,
            password=scene.ap_password,
        )
        return {"FINISHED"}


class WM_OT_AP_Disconnect(bpy.types.Operator):
    bl_label  = "Disconnect from Archipelago"
    bl_idname = "wm.ap_disconnect"

    def execute(self, context):
        ap_client.disconnect()
        return {"FINISHED"}
