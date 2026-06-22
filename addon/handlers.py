import bpy
import os
import tempfile
from . import ap_client, ids, similarity, progress, unlocked, thresholds
from bpy.app.handlers import persistent

_msgbus_owner = object()


def timer_popup(message: str):
    bpy.app.timers.register(
        # Use a timer to defer the call until context is available.
        # Returning None stops the timer from repeating
        lambda: bpy.ops.wm.ap_popup("INVOKE_DEFAULT", message = message) and None,
        first_interval = 0.0
    )
    print(f"[Blender AP] {message}")


def _update_similarity_percent(target_name: str):
    target = bpy.data.images.get(target_name)
    if not target:
        timer_popup(f"Target image \"{target_name}\" not found.")
        return

    tmp_path = os.path.join(tempfile.gettempdir(), "ap_blender_render.png")
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    bpy.data.images["Render Result"].save_render(tmp_path, scene = scene)

    render = bpy.data.images.load(tmp_path)

    try:
        score = similarity.compare_images(render, target)
        progress.percent = score
        print(f"[Blender AP] Similarity: {score:.3f}%")
    finally:
        bpy.data.images.remove(render)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _update_checks():
    for i, (threshold, checked) in enumerate(sorted(thresholds.items())):
        if progress.percent >= threshold:
            if not checked:
                location_name = ids.LOCATIONS[i]
                location_id = ids.LOCATION_TO_ID.get(location_name)
                thresholds[threshold] = True
                ap_client.send_check(location_id)
        else:
            break


def _update_goal():
    if progress.percent >= progress.goal_percent:
        ap_client.send_goal_complete()


@persistent
def _on_render_complete(scene, depsgraph):
    target_name = scene.ap_target_image
    if not target_name:
        timer_popup("No target image selected.")
        return
    
    # A timer for each function does not guarantee they run in order,
    # so they are put into one function so that they are guaranteed to run in this order
    def _update_state():
        _update_similarity_percent(target_name)
        _update_checks()
        _update_goal()

    bpy.app.timers.register(_update_state, first_interval=0.0)


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
        if obj and obj.mode == mode and not unlocked[item]:
            bpy.ops.object.mode_set(mode="OBJECT")
            unlock_text = item.name.replace("_", " ").title()
            if item == ids.Item.GREASE_PENCIL_MODES:
                timer_popup(f"{unlock_text} are locked.")
            else:
                unlock_text = item.name.replace("_", " ").title()
                timer_popup(f"{unlock_text} is locked.")
            break


@persistent
def _materials_locked(scene = None, depsgraph = None):
    if unlocked[ids.Item.MATERIALS]:
        return

    obj = bpy.context.active_object
    if obj and hasattr(obj.data, "materials") and len(obj.data.materials) > 0:
        obj.data.materials.clear()
        timer_popup("Materials are locked.")


@persistent
def _clear_materials(scene, depsgraph):
    if unlocked[ids.Item.MATERIALS]:
        return
    
    for obj in bpy.data.objects:
        if hasattr(obj.data, "materials"):
            obj.data.materials.clear()


@persistent
def _modifiers_locked(scene = None, depsgraph = None):
    if unlocked[ids.Item.MODIFIERS]:
        return
    
    obj = bpy.context.active_object
    if obj and obj.modifiers:
        obj.modifiers.clear()
        timer_popup("Modifiers are locked.")


@persistent
def _world_shaders_locked(scene = None, depsgraph = None):
    if unlocked[ids.Item.WORLD_SHADERS]:
        return
    
    bpy.context.scene.world = None
    timer_popup("World Shaders are locked.")


@persistent
def _clear_world_shaders(scene, depsgraph):
    if unlocked[ids.Item.WORLD_SHADERS]:
        return
    
    bpy.context.scene.world = None


@persistent
def _import_disabled(scene, depsgraph):
    bpy.ops.object.delete()
    timer_popup("Importing is disabled.")


_import_op_prefixes = (
    "IMPORT_SCENE_OT_",
    "IMPORT_MESH_OT_",
    "IMPORT_CURVE_OT_",
    "IMPORT_ANIM_OT_",
    "WM_OT_obj_import",
    "WM_OT_fbx_import",
    "WM_OT_stl_import",
    "WM_OT_usd_import",
    "WM_OT_alembic_import",
    "WM_OT_collada_import",
    "WM_OT_gltf_import",
)

_last_handled_import_op = None

@persistent
def _file_import_disabled(scene, depsgraph):
    global _last_handled_import_op

    ops = bpy.context.window_manager.operators
    if not ops:
        return

    last_op = ops[-1]
    idname = last_op.bl_idname

    if not idname.startswith(_import_op_prefixes):
        return

    if last_op == _last_handled_import_op:
        return

    _last_handled_import_op = last_op

    for obj in bpy.context.selected_objects:
        bpy.data.objects.remove(obj)

    timer_popup("Importing is disabled.")


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
    (bpy.app.handlers.load_post, _subscribe),
    (bpy.app.handlers.load_post, _clear_materials),
    (bpy.app.handlers.load_post, _clear_world_shaders),
    (bpy.app.handlers.depsgraph_update_post, _file_import_disabled),
    (bpy.app.handlers.depsgraph_update_post, _modifiers_locked),
    (bpy.app.handlers.blend_import_post, _import_disabled),
    (bpy.app.handlers.render_complete, _on_render_complete),
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
    