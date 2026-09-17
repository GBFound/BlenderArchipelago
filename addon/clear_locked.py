import bpy
from . import ids, persist


def all_async():
    bpy.app.timers.register(all)


def all():
    _clear_materials()
    _clear_world_shaders()
    _clear_compositor()


def _clear_materials():
    scene = bpy.context.scene
    if not scene.ap_has_connected_before:
        return
    if persist.ap_item_counts[ids.Item.MATERIALS]:
        return
    
    for obj in bpy.data.objects:
        if hasattr(obj.data, "materials"):
            obj.data.materials.clear()


def _clear_world_shaders():
    scene = bpy.context.scene
    if not scene.ap_has_connected_before:
        return
    if persist.ap_item_counts[ids.Item.WORLD_SHADERS]:
        return
    
    bpy.context.scene.world = None


def _clear_compositor():
    scene = bpy.context.scene
    if not scene.ap_has_connected_before:
        return
    if persist.ap_item_counts[ids.Item.COMPOSITOR]:
        return

    bpy.context.scene.compositing_node_group = None
