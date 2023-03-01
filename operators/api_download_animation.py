import bpy
import asyncio
import os
import json
from mathutils import Quaternion, Matrix
import gzip

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
        download_path = os.path.join(api.download_dir, 'animation.heat')

        # download file from heat
        dl_url = 'https://1646-public-storage.s3.us-west-1.amazonaws.com/Test_v4_FistPump.heat'
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

        armature = bpy.context.scene.objects['Armature']

        # apply animation to armature as a new action
        with gzip.open(download_path, 'rb') as f:
            data = json.load(f)
            action = bpy.data.actions.new("heat_action")

            pose = {}
            def fill_pose(pose, joint):
                m = joint['local_matrix']
                # blender is row major
                pose[joint['name']] = Matrix([m[0:4], m[4:8], m[8:12], m[12:16]]).transposed()
                for child in joint['children']:
                    fill_pose(pose, child)

            fill_pose(pose, data['pose'])

            for track in data['tracks']:
                data_path = 'pose.bones["{0}"].rotation_quaternion'.format(track['name'])
                quaternions = []
                for t, value in track['keys']:
                    bone_rest_quat = scene_armature.bones[track['name']].matrix_local.to_quaternion()
                    # manage root bone (quaternions in blender are WXYZ while heat uses XYZW)
                    if not armature.pose.bones[track['name']].parent:
                        quaternions.append([t,  armature.matrix_world.to_quaternion() @ bone_rest_quat.inverted() @ Quaternion((value[3], value[0], value[1], value[2]))])
                    else:
                        quaternions.append([t, bone_rest_quat.inverted() @ Quaternion((value[3], value[0], value[1], value[2]))])

                # fix singularity
                for j in range(1, len(quaternions)):
                    if quaternions[j][1].dot(quaternions[j-1][1]) < 0:
                        quaternions[j][1] = -quaternions[j][1]

                # add keyframes
                for i in range(0, 4):
                    curve = action.fcurves.new(data_path, index=i)

                    for t, q in quaternions:
                        fps = bpy.context.scene.render.fps
                        frame = t * fps
                        curve.keyframe_points.insert(frame, q[i])
                    curve.update()

            scene_armature.animation_data.action = action


    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
