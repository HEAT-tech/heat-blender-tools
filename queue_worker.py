import bpy
import time
from .simple_queue import SimpleQueue

def work_queue():
    queue = SimpleQueue('heat_queue.db')
    task = queue.pop()
    if task is None:
        return 0.5

    if task['task'] == "login":
        auth_token = task["data"]["auth_token"]

        this_plugin_name = __name__.split(".")[0]
        bpy.context.preferences.addons[this_plugin_name].preferences.heat_user_api_key = auth_token
        bpy.ops.heat.panic_reset()
    elif task['task'] == "downloadMovement":
        bpy.context.window_manager.heat_preview_webui = True
        movement = task["data"]
        movement_index = find_animation_index_by_id(movement['movementID'])

        if movement_index < 0:
            new_movement = bpy.context.scene.heat_animation_results_list.add()
            new_movement.name = movement['name']
            new_movement.movement_id = movement['movementID']
            new_movement.description = movement['description']
            new_movement.download_url = movement['downloadUrl']
            new_movement.preview_image_url = movement['previewImageUrl']
            new_movement.url = movement['url']
            movement_index = len(bpy.context.scene.heat_animation_results_list.items())-1

        bpy.context.scene.heat_animation_results_list_index = movement_index

        # handle style of import (selection vs armature and model)
        if 'exportTo' in movement:
            if movement['exportTo'] == 1:
                bpy.ops.heat.import_t69h()
            elif movement['exportTo'] == 2:
                bpy.ops.heat.import_t69h_armature()

        bpy.context.view_layer.update()
        time.sleep(0.125)
        queue.push('loadMovement', '')
    elif task['task'] == 'loadMovement':
        # download animation after movement has been set as active
        # necessary in order to not lose context
        if bpy.context.window_manager.heat_preview_texture_loading:
            return 0.25

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                override = bpy.context.copy()
                override['area'] = area
                override['region'] = area.regions[0]
                bpy.ops.heat.download_animation(override, 'INVOKE_DEFAULT')
                break
    elif task['task'] == "addCube":
        bpy.ops.mesh.primitive_cube_add()

    queue.set_completed(task["id"])
    return 0.5


def find_animation_index_by_id(id):
    animation_list = bpy.context.scene.heat_animation_results_list

    for index, item in enumerate(animation_list):
        if item.movement_id == id:
            return index

    # If no match found, return -1 or any appropriate value
    return -1