import bpy
import os
import tempfile
from . import ap_client, ids, similarity, progress, unlocked, thresholds

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
        progress["percent"] = score
        print(f"[Blender AP] Similarity: {score:.3f}%")
    finally:
        bpy.data.images.remove(render)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _update_checks():
    for i, (threshold, checked) in enumerate(sorted(thresholds.items())):
        if progress["percent"] >= threshold:
            if not checked:
                location_name = ids.LOCATIONS[i]
                location_id = ids.LOCATION_NAME_TO_ID.get(location_name)
                thresholds[threshold] = True
                ap_client.send_check(location_id)
        else:
            break


def _update_goal():
    if progress["percent"] >= progress["goal_percent"]:
        ap_client.send_goal_complete()


def on_render_complete(scene, depsgraph = None):
    target_name = scene.ap_target_image
    if not target_name:
        timer_popup("No target image selected.")
        return
    
    # A timer for each function does not guarantee they run in order, so they are put into one function so that they are guaranteed to run in this order
    def _update_state():
        _update_similarity_percent(target_name)
        _update_checks()
        _update_goal()

    bpy.app.timers.register(_update_state, first_interval=0.0)


def mode_locked(scene = None, depsgraph = None):
    obj = bpy.context.active_object
    modes = {
        "EDIT": "edit_mode",
        "SCULPT": "sculpt_mode",
        "VERTEX_PAINT": "vertex_paint_mode",
        "WEIGHT_PAINT": "weight_paint_mode",
        "TEXTURE_PAINT": "texture_paint_mode",
    }

    if not obj:
        return

    for mode, unlock in modes.items():
        if obj.mode == mode and not unlocked[unlock]:
            bpy.ops.object.mode_set(mode="OBJECT")
            unlock_text = unlock.replace("_", " ").title()
            timer_popup(f"{unlock_text} is locked.")
            break

 
def register():
    bpy.app.handlers.render_complete.append(on_render_complete)
    bpy.app.handlers.undo_post.append(mode_locked)
    bpy.msgbus.subscribe_rna(
        key=(bpy.types.Object, "mode"),
        owner=_msgbus_owner,
        args=(),
        notify=mode_locked,
    )
 
 
def unregister():
    bpy.msgbus.clear_by_owner(_msgbus_owner)
    bpy.app.handlers.undo_post.remove(mode_locked)
    bpy.app.handlers.render_complete.remove(on_render_complete)
    