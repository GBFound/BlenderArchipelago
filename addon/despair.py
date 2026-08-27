import bpy
import random
from . import unlocks

_TEMP_UNLOCK_DURATION_SECONDS = 30


def schedule_despair():
    bpy.app.timers.register(_despair)


def _despair():
    unlocks.temp_unlock_all_tools(_TEMP_UNLOCK_DURATION_SECONDS)
    mesh = _select_single_mesh()
    bpy.context.view_layer.objects.active = mesh

    _simple_subdiv_to_target(mesh)
    _apply_modifiers(mesh)
    _delete_random_face_region(mesh)
    _set_cloth(mesh)
    _play_animation()

    _view_selected()


def _select_single_mesh() -> bpy.types.Object:
    selected = bpy.context.selected_objects

    if len(selected) == 1 and selected[0].type == "MESH":
        # Single mesh already selected
        return selected[0]

    elif len(selected) > 1:
        # Multiple objects selected, so filter down to meshes and pick one at random
        meshes = [obj for obj in selected if obj.type == "MESH"]
        if meshes:
            selected = random.choice(meshes)
            for obj in selected:
                obj.select_set(False)
            selected.select_set(True)
            return selected
        else:
            # No mesh selected
            return _pick_from_scene_or_create()

    else:
        # No mesh selected
        return _pick_from_scene_or_create()


def _pick_from_scene_or_create() -> bpy.types.Object:
    mesh_objs = [obj for obj in bpy.context.view_layer.objects if obj.type == "MESH"]
    if mesh_objs:
        selected = random.choice(mesh_objs)
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        selected.select_set(True)
        return selected
    else:
        # No mesh in scene
        return _create_default_cube()


def _create_default_cube() -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.active_object

    return cube


def _simple_subdiv_to_target(obj, target=2048, max_levels=6):
    base_faces = len(obj.data.polygons)
    if base_faces >= target:
        return

    modifier = obj.modifiers.new(name="AutoSimpleSubdiv", type="SUBSURF")
    modifier.subdivision_type = "SIMPLE"
    modifier.levels = 0
    modifier.render_levels = 0

    depsgraph = bpy.context.evaluated_depsgraph_get()

    while modifier.levels < max_levels:  # In case mesh has 0 faces
        modifier.levels += 1
        depsgraph.update()
        current_faces = _get_face_count(obj, depsgraph)

        if current_faces >= target:
            modifier.levels -= 1
            if modifier.levels == 0:
                obj.modifiers.remove(modifier)
            return


def _get_face_count(obj, depsgraph) -> int:
    evaluated_obj = obj.evaluated_get(depsgraph)  # Get object after all its modifiers and stuff have been applied.
    return len(evaluated_obj.data.polygons)


def _apply_modifiers(obj):
    for modifier in obj.modifiers:
        try:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        except RuntimeError:
            print(f"Error applying modifier {modifier.name} to object {obj.name}.")


def _delete_random_face_region(obj):
    if obj.hide_get():
        obj.hide_set(False)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")

    mesh_data = obj.data
    random_face = random.choice(mesh_data.polygons)  # bpy.ops.mesh.select_random can't guarantee exactly one face
    random_face.select = True
    mesh_data.update()

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_more()
    bpy.ops.mesh.select_more()
    bpy.ops.mesh.delete(type="FACE")
    bpy.ops.object.mode_set(mode="OBJECT")


def _set_cloth(obj):
    cloth_modifier = obj.modifiers.new(name="Cloth", type="CLOTH")
    cloth_settings = cloth_modifier.settings
    cloth_settings.effector_weights.gravity = 0
    cloth_settings.use_pressure = True
    cloth_settings.use_pressure_volume = True
    cloth_settings.air_damping = 0.2

    fcurve = cloth_settings.driver_add("uniform_pressure_force")
    driver = fcurve.driver
    driver.type = "SCRIPTED"
    driver.expression = "-2*(sin(0.3*frame)+0.6)"

    var = driver.variables.new()
    var.name = "frame"
    var.type = "SINGLE_PROP"

    target = var.targets[0]
    target.id_type = "SCENE"
    target.id = bpy.context.scene
    target.data_path = "frame_current"


def _play_animation():
    bpy.context.scene.frame_current = 1
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 250
    bpy.ops.screen.animation_play()


def _view_selected():
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == 'WINDOW':
                        with bpy.context.temp_override(area=area, region=region):
                            bpy.ops.view3d.view_selected()
