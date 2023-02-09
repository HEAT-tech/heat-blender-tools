import bpy
import asyncio
import os
import json

from .. import services


class APIDownloadAnimationOperator(bpy.types.Operator):
    """Download Heat Animation"""
    bl_idname = "heat.download_animation"
    bl_label = "Download Heat Animation"

    def execute(self, context):
        async_task = asyncio.ensure_future(self.download_file(context))
        services.ensure_async_loop()
        return {'FINISHED'}

    async def download_file(self, context):
        api = services.HeatAPIClient()

        active_movement_index = context.scene.heat_animation_results_list_index
        active_movement = context.scene.heat_animation_results_list[active_movement_index]
        download_path = os.path.join(api.download_dir, 'download.gltf')

        # download file from heat
        dl_url = 'https://arbztjwhu7.execute-api.us-west-1.amazonaws.com/dev/v1/movements/a0026ddb-a7e1-484d-8b6c-fa3cfd6d407e/download'
        await api.download_file(dl_url, download_path)
        # await api.download_file(active_movement.download_url, download_path)

        # import T69H and/or apply animation fcurves from response
        active_object = bpy.context.active_object
        try:
            scene_armature = bpy.data.armatures[0]
        except:
            scene_armature = None

        # import T69H if no object is currently selected or no armature in scene
        if active_object is None and scene_armature is None:
            bpy.ops.heat.import_t69h()
            scene_armature = bpy.data.armatures[0]
        elif active_object is not None:
            scene_armature = active_object

        # apply animation to armature as a new action
        with open(download_path, "r") as f:
            data = json.load(f)
            action = bpy.data.actions.new("heat_action")

            for bone_keys in data:
                name = bone_keys["name"]
                attr = bone_keys["attr"]
                keys = bone_keys["keys"]

                if attr == 'translation':
                    attr = 'location'

                if attr == 'rotation':
                    attr = 'rotation_quaternion'

                data_path = f'pose.bones["{name}"].{attr}'

                for key in keys:
                    fps = bpy.context.scene.render.fps
                    frame = key[0] * fps
                    matrix = key[1]
                    if attr == 'location':
                        matrix = [matrix[0] * 0.001, matrix[1] * 0.001 , matrix[2] * 0.001]
                    if attr == 'rotation_quaternion':
                        matrix = [-matrix[3], matrix[0], matrix[2], matrix[1]]

                    for axis, value in enumerate(matrix):
                        fcurve = action.fcurves.find(data_path=data_path, index=axis)
                        if fcurve == None:
                            fcurve = action.fcurves.new(data_path=data_path, index=axis)

                        fcurve.keyframe_points.insert(frame, value)

            scene_armature.animation_data.action = action


    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
