# Adapted from Andrei Davydov

import bpy
from bpy.app.handlers import persistent
import os

# --- Config ---
IMAGE_FOLDER = os.path.join(os.path.dirname(__file__), "explosion")
NUM_FRAMES = 17
FPS = 24

# --- Helper functions ---
def get_images():
    if not os.path.isdir(IMAGE_FOLDER):
        return []
    files = sorted([f for f in os.listdir(IMAGE_FOLDER)
                    if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    return [os.path.join(IMAGE_FOLDER, f) for f in files[:NUM_FRAMES]]

# --- Animation function ---
def spawn_animated_ref_image():
    bpy.app.timers.register(spawn_animated_ref_image)


def _spawn_animated_ref_image():
    images = get_images()
    if not images:
        print(f"[Explosion] No images found in {IMAGE_FOLDER}")
        return None

    # Load first image
    img = bpy.data.images.load(bpy.path.abspath(images[0]))

    # Create reference image empty
    ref_obj = bpy.data.objects.new("GoodbyeRef", None)
    ref_obj.empty_display_type = 'IMAGE'
    ref_obj.empty_display_size = 20
    ref_obj.data = img
    bpy.context.collection.objects.link(ref_obj)

    # Place in front of the viewport camera
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            region_3d = area.spaces.active.region_3d
            if region_3d.view_perspective == 'CAMERA':
                camera = bpy.context.scene.camera
                ref_obj.location = camera.matrix_world.translation + camera.matrix_world.col[2].xyz * -10
                ref_obj.rotation_euler = camera.rotation_euler
            else:
                ref_obj.location = region_3d.view_location
                ref_obj.rotation_euler = region_3d.view_rotation.to_euler()
            break
    
    # Animation state
    frame_index = 0

    # Timer callback to cycle frames
    def update_frame():
        nonlocal frame_index
        frame_index += 1
        if frame_index >= len(images):
            # Delete object at end
            bpy.data.objects.remove(ref_obj, do_unlink=True)
            return None  # stop timer
        # Load next frame
        img_path = bpy.path.abspath(images[frame_index])
        img = bpy.data.images.load(img_path)
        ref_obj.data = img
        return 1 / FPS  # run again in 1/30 sec

    bpy.app.timers.register(update_frame)
