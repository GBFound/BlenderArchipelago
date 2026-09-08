import bpy
from . import ids, persist, unlocks


def enforce_async():
    bpy.app.timers.register(enforce)


def enforce(scene=None):
    _enforce_camera_settings(scene)
    _enforce_render_border(scene)


def _enforce_camera_settings(scene):
    if scene is None:
        scene = bpy.context.scene

    camera = scene.camera
    if not camera:
        return 

    if not persist.ap_target_image_filepath:
        return
    
    image = bpy.data.images.get(persist.ap_target_image)
    if image is None:
        image = bpy.data.images.load(persist.ap_target_image_filepath)

    scene.render.resolution_x = image.size[0]
    scene.render.resolution_y = image.size[1]

    if camera.data.background_images:
        bg = camera.data.background_images[0]
    else:
        bg = camera.data.background_images.new()
    bg.image = image
    camera.data.show_background_images = True
    camera.data.background_images[0].alpha = 1


def _enforce_render_border(scene):
    if scene is None:
        scene = bpy.context.scene

    scene.render.use_border = True
    scene.render.border_min_x = 0
    scene.render.border_min_y = 0
    progressive_render_width_value = unlocks.get_item_count(ids.Item.PROGRESSIVE_RENDER_WIDTH)
    progressive_render_height_value = unlocks.get_item_count(ids.Item.PROGRESSIVE_RENDER_HEIGHT)
    progressive_render_width_max = unlocks.progressive_render_width_max
    progressive_render_height_max = unlocks.progressive_render_height_max
    scene.render.border_max_x = (1 + progressive_render_width_value) / (1 + progressive_render_width_max)
    scene.render.border_max_y = (1 + progressive_render_height_value) / (1 + progressive_render_height_max)
