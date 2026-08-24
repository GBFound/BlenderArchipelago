import bpy
import os
import tempfile
from bpy.app.handlers import persistent
from . import ap_client, ap_data_package, ids, persist, popup, progress, similarity, thresholds, unlocks


_msgbus_owner = object()


def _update_similarity_percent(target_name: str):
    target = bpy.data.images.get(target_name)
    if not target:
        popup.enqueue(f"Target image \"{target_name}\" not found.")
        return

    tmp_path = os.path.join(tempfile.gettempdir(), "ap_blender_render.png")
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    bpy.data.images["Render Result"].save_render(tmp_path, scene = scene)

    render = bpy.data.images.load(tmp_path)

    try:
        score = similarity.compare_images(render, target)
        bpy.context.scene.difference = score - bpy.context.scene.current_percent
        persist.difference = bpy.context.scene.difference
        bpy.context.scene.current_percent = score
        persist.current_percent = score
        print(f"[Blender AP] Similarity: {score:.3f}%")
    finally:
        bpy.data.images.remove(render)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _update_checks():
    for i, (threshold, checked) in enumerate(sorted(thresholds.data.items())):
        if bpy.context.scene.current_percent >= threshold:
            if not checked:
                location_id = ids.BASE_ID + i
                thresholds.data[threshold] = True
                ap_client.send_check(location_id)
        else:
            break


def _update_goal():
    if bpy.context.scene.current_percent >= progress.goal_percent:
        for threshold in thresholds.data:
            thresholds.data[threshold] = True
        ap_client.send_goal_complete()


@persistent
def _update_state(scene, depsgraph):
    target_name = scene.ap_target_image
    if not target_name:
        popup.enqueue("No target image selected.")
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


@persistent
def _deathlink_redo(scene, depsgraph):
    ap_client.send_deathlink("redo")


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
        if obj and obj.mode == mode and not unlocks.get_item_count(item):
            bpy.ops.object.mode_set(mode="OBJECT")
            unlock_text = popup.item_to_unlock_text(item)
            if item == ids.Item.GREASE_PENCIL_MODES:
                popup.enqueue(f"{unlock_text} are locked.")
            else:
                popup.enqueue(f"{unlock_text} is locked.")
            break


@persistent
def _materials_locked(scene = None, depsgraph = None):
    if unlocks.get_item_count(ids.Item.MATERIALS):
        return

    obj = bpy.context.active_object
    if obj and hasattr(obj.data, "materials") and len(obj.data.materials) > 0:
        obj.data.materials.clear()
        popup.enqueue("Materials are locked.")


@persistent
def _clear_materials(scene = None, depsgraph = None):
    if unlocks.get_item_count(ids.Item.MATERIALS):
        return
    
    for obj in bpy.data.objects:
        if hasattr(obj.data, "materials"):
            obj.data.materials.clear()


@persistent
def _modifiers_locked(scene, depsgraph):
    if unlocks.get_item_count(ids.Item.MODIFIERS):
        return
    
    obj = bpy.context.active_object
    if obj and obj.modifiers:
        if (_clear_other_modifiers(obj)):
            popup.enqueue("Modifiers are locked.")


def _clear_other_modifiers(obj) -> bool:
    did_clear = False
    for mod in list(obj.modifiers):  # list() to avoid mutating while iterating
        if mod.type != 'NODES':
            obj.modifiers.remove(mod)
            did_clear = True

    return did_clear


@persistent
def _geometry_nodes_locked(scene, depsgraph):
    if unlocks.get_item_count(ids.Item.GEOMETRY_NODES):
        return
    
    obj = bpy.context.active_object
    if obj and obj.modifiers:
        if (_clear_geometry_nodes(obj)):
            popup.enqueue("Geometry Nodes are locked.")


def _clear_geometry_nodes(obj):
    did_clear = False
    for mod in list(obj.modifiers):  # list() to avoid mutating while iterating
        if mod.type == 'NODES':
            obj.modifiers.remove(mod)
            did_clear = True

    return did_clear


@persistent
def _world_shaders_locked(scene = None, depsgraph = None):
    if unlocks.get_item_count(ids.Item.WORLD_SHADERS):
        return
    
    if bpy.context.scene.world:
        bpy.context.scene.world = None
        popup.enqueue("World Shaders are locked.")


@persistent
def _clear_world_shaders(scene = None, depsgraph = None):
    if unlocks.get_item_count(ids.Item.WORLD_SHADERS):
        return
    
    bpy.context.scene.world = None


@persistent
def _compositor_locked(scene = None, depsgraph = None):
    if unlocks.get_item_count(ids.Item.COMPOSITOR):
        return

    if bpy.context.scene.compositing_node_group:
        bpy.context.scene.compositing_node_group = None
        popup.enqueue("Compositor is locked.")


@persistent
def _clear_compositor(scene = None, depsgraph = None):
    if unlocks.get_item_count(ids.Item.COMPOSITOR):
        return

    bpy.context.scene.compositing_node_group = None


@persistent
def _persist_to_blender_properties(scene, depsgraph):
    for item, count in persist.item_counts.items():
        unlocks.set_item_count(item, count)

    ap_data_package.save_data_package(persist.ap_data_package)

    for field in persist.SIMPLE_SCENE_FIELDS:
        value = getattr(persist, field)
        setattr(bpy.context.scene, field, value)


@persistent
def _blender_properties_to_persist(scene, depsgraph):
    for item in persist.item_counts:
        persist.item_counts[item] = unlocks.get_item_count(item)

    persist.ap_data_package = ap_data_package.load_data_package()
    
    for field in persist.SIMPLE_SCENE_FIELDS:
        value = getattr(bpy.context.scene, field)
        setattr(persist, field, value)


@persistent
def _import_disabled(scene, depsgraph):
    for obj in bpy.context.selected_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    popup.enqueue("Importing is disabled in Archipelago.")


@persistent
def clear_locked_features(scene = None, depsgraph = None):
    _clear_materials()
    _clear_world_shaders()
    _clear_compositor()


def schedule_use_render_border():
    bpy.app.timers.register(use_render_border)


@persistent
def use_render_border(scene = None, depsgraph = None):
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


_subscriptions = (
    (bpy.types.Object, "mode",                   _mode_locked),
    (bpy.types.Object, "active_material",        _materials_locked),
    (bpy.types.Scene,  "world",                  _world_shaders_locked),
    (bpy.types.Scene,  "compositing_node_group", _compositor_locked),
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
    (bpy.app.handlers.load_post,             _blender_properties_to_persist),
    (bpy.app.handlers.load_post,             clear_locked_features),
    (bpy.app.handlers.depsgraph_update_post, _modifiers_locked),
    (bpy.app.handlers.depsgraph_update_post, _geometry_nodes_locked),
    # (bpy.app.handlers.blend_import_post,     _import_disabled),  Too annoying
    (bpy.app.handlers.render_init,           use_render_border),
    (bpy.app.handlers.render_complete,       _update_state),
    (bpy.app.handlers.undo_post,             _deathlink_undo),
    (bpy.app.handlers.redo_post,             _deathlink_redo),
    (bpy.app.handlers.undo_post,             _persist_to_blender_properties),
    (bpy.app.handlers.redo_post,             _persist_to_blender_properties),
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
    