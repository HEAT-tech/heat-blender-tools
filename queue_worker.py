import bpy
from .simple_queue import SimpleQueue

def work_queue():
    queue = SimpleQueue('heat_queue.db')
    task = queue.pop()
    if task is None:
        return 0.5

    print(task)
    if task['task'] == "login":
        print(task["data"])
        print(task["data"]["auth_token"])
        auth_token = task["data"]["auth_token"]

        this_plugin_name = __name__.split(".")[0]
        bpy.context.preferences.addons[this_plugin_name].preferences.heat_user_api_key = auth_token
        bpy.ops.heat.panic_reset()

    else:
        bpy.ops.mesh.primitive_cube_add()
    return 0.5