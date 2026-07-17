import bpy
import os
import random
import tempfile
from bpy.app.handlers import persistent
from . import ap_client, explosion, ids, similarity, utils, progress, unlocks, thresholds


_msgbus_owner = object()


def _update_similarity_percent(target_name: str):
    target = bpy.data.images.get(target_name)
    if not target:
        utils.queue_popup(f"Target image \"{target_name}\" not found.")
        return

    tmp_path = os.path.join(tempfile.gettempdir(), "ap_blender_render.png")
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    bpy.data.images["Render Result"].save_render(tmp_path, scene = scene)

    render = bpy.data.images.load(tmp_path)

    try:
        score = similarity.compare_images(render, target)
        progress.current_percent = score
        print(f"[Blender AP] Similarity: {score:.3f}%")
    finally:
        bpy.data.images.remove(render)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _update_checks():
    for i, (threshold, checked) in enumerate(sorted(thresholds.data.items())):
        if progress.current_percent >= threshold:
            if not checked:
                location_id = ids.BASE_ID + i
                thresholds.data[threshold] = True
                ap_client.send_check(location_id)
        else:
            break


def _update_goal():
    if progress.current_percent >= progress.goal_percent:
        for threshold in thresholds.data:
            thresholds.data[threshold] = True
        ap_client.send_goal_complete()


@persistent
def _update_state(scene, depsgraph):
    target_name = scene.ap_target_image
    if not target_name:
        utils.queue_popup("No target image selected.")
        return
    
    # A timer for each function does not guarantee they run in order,
    # so they are put into one function so that they are guaranteed to run in this order
    def _update():
        _update_similarity_percent(target_name)
        _update_checks()
        _update_goal()

    bpy.app.timers.register(_update)


@persistent
def _deathlink_undo(scene, depsgraph):
    ap_client.send_deathlink("undo")
    explosion.spawn_animated_ref_image()


@persistent
def _deathlink_redo(scene, depsgraph):
    ap_client.send_deathlink("redo")
    explosion.spawn_animated_ref_image()


@persistent
def _mode_locked(scene = None, depsgraph = None):
    obj = bpy.context.active_object
    modes = {
        "EDIT"          : ids.Item.EDIT_MODE,
        "SCULPT"        : ids.Item.SCULPT_MODE,
        "VERTEX_PAINT"  : ids.Item.VERTEX_PAINT_MODE,
        "WEIGHT_PAINT"  : ids.Item.WEIGHT_PAINT_MODE,
        "TEXTURE_PAINT" : ids.Item.TEXTURE_PAINT_MODE,

        "SCULPT_GREASE_PENCIL" : ids.Item.GREASE_PENCIL_MODES,
        "PAINT_GREASE_PENCIL"  : ids.Item.GREASE_PENCIL_MODES,
        "WEIGHT_GREASE_PENCIL" : ids.Item.GREASE_PENCIL_MODES,
        "VERTEX_GREASE_PENCIL" : ids.Item.GREASE_PENCIL_MODES,
    }

    for mode, item in modes.items():
        if obj and obj.mode == mode and not unlocks.data[item]:
            bpy.ops.object.mode_set(mode="OBJECT")
            unlock_text = item.name.replace("_", " ").title()
            if item == ids.Item.GREASE_PENCIL_MODES:
                utils.queue_popup(f"{unlock_text} are locked.")
            else:
                unlock_text = item.name.replace("_", " ").title()
                utils.queue_popup(f"{unlock_text} is locked.")
            break


@persistent
def _materials_locked(scene = None, depsgraph = None):
    if unlocks.data[ids.Item.MATERIALS]:
        return

    obj = bpy.context.active_object
    if obj and hasattr(obj.data, "materials") and len(obj.data.materials) > 0:
        obj.data.materials.clear()
        utils.queue_popup("Materials are locked.")


@persistent
def _clear_materials(scene, depsgraph):
    if unlocks.data[ids.Item.MATERIALS]:
        return
    
    for obj in bpy.data.objects:
        if hasattr(obj.data, "materials"):
            obj.data.materials.clear()


@persistent
def _modifiers_locked(scene, depsgraph):
    if unlocks.data[ids.Item.MODIFIERS]:
        return
    
    obj = bpy.context.active_object
    if obj and obj.modifiers:
        obj.modifiers.clear()
        utils.queue_popup("Modifiers are locked.")


@persistent
def _world_shaders_locked(scene = None, depsgraph = None):
    if unlocks.data[ids.Item.WORLD_SHADERS]:
        return
    
    if bpy.context.scene.world:
        bpy.context.scene.world = None
        utils.queue_popup("World Shaders are locked.")


@persistent
def _clear_world_shaders(scene, depsgraph):
    if unlocks.data[ids.Item.WORLD_SHADERS]:
        return
    
    bpy.context.scene.world = None


@persistent
def _import_disabled(scene, depsgraph):
    bpy.ops.object.delete()
    utils.queue_popup("Importing is disabled in Archipelago.")


@persistent
def _use_render_border(scene = None, depsgraph = None):
    scene.render.use_border = True
    scene.render.border_min_x = 0
    scene.render.border_min_y = 0
    progressive_render_width_value = unlocks.data.get(ids.Item.PROGRESSIVE_RENDER_WIDTH)
    progressive_render_height_value = unlocks.data.get(ids.Item.PROGRESSIVE_RENDER_HEIGHT)
    # TODO Currently / 3 to allow redundant progressive items because there is no logic to ensure they spawn early enough
    scene.render.border_max_x = (1 + progressive_render_width_value) / 3  # TODO Use YAML values once implemented
    scene.render.border_max_y = (1 + progressive_render_height_value) / 3  # TODO Use YAML values once implemented


_subscriptions = (
    (bpy.types.Object, "mode",            _mode_locked),
    (bpy.types.Object, "active_material", _materials_locked),
    (bpy.types.Scene,  "world",           _world_shaders_locked),
)


@persistent
def _subscribe(scene = None, depsgraph = None):
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    for rna_struct, property, handler in _subscriptions:
        bpy.msgbus.subscribe_rna(
            key=(rna_struct, property),
            owner=_msgbus_owner,
            args=(),
            notify=handler,
        )


_handlers = [
    (bpy.app.handlers.load_post,             _subscribe),
    (bpy.app.handlers.load_post,             _clear_materials),
    (bpy.app.handlers.load_post,             _clear_world_shaders),
    (bpy.app.handlers.depsgraph_update_post, _modifiers_locked),
    (bpy.app.handlers.blend_import_post,     _import_disabled),
    (bpy.app.handlers.render_init,           _use_render_border),
    (bpy.app.handlers.render_complete,       _update_state),
    (bpy.app.handlers.undo_post,             _deathlink_undo),
    (bpy.app.handlers.redo_post,             _deathlink_redo),
]
for _, _, handler in _subscriptions:
    _handlers.append((bpy.app.handlers.undo_post, handler))
    _handlers.append((bpy.app.handlers.redo_post, handler))


def register():
    for handler_list, handler in _handlers:
        handler_list.append(handler)
    _subscribe()
 
 
def unregister():
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    for handler_list, handler in reversed(_handlers):
        handler_list.remove(handler)
    