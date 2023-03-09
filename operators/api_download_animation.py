import bpy
import asyncio
import os
import json
from mathutils import Quaternion, Matrix, Vector
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
        context.scene.heat_animation_id_downloading = True
        await api.download_file(active_movement.download_url, download_path)

        # import T69H and/or apply animation fcurves from response
        active_object = bpy.context.active_object
        armature =  bpy.context.scene.objects.find('Armature')

        if active_object is not None:
            if active_object.type == 'ARMATURE':
                armature = active_object
            elif active_object.parent.type == 'ARMATURE':
                armature = active_object.parent
        elif armature == -1:
            bpy.ops.heat.import_t69h()
            armature = bpy.context.scene.objects['Armature']

        if armature.animation_data is None:
            armature.animation_data_create()

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
                if track['attr'] == 'translation':
                    data_path = 'pose.bones["{0}"].location'.format(track['name'])
                    translation_curves = []

                    for i in range(0, 3):
                        curve = action.fcurves.new(data_path, index=i)
                        translation_curves.append(curve)

                    for key in track['keys']:
                        t = key[0]
                        values = Vector((key[1][0], -key[1][2], key[1][1]))
                        pt = pose[track['name']].to_translation()
                        pose_translation = Vector((pt[0], -pt[2], pt[1]))

                        if not armature.pose.bones[track['name']].parent:
                           values -= armature.matrix_world.to_translation() - pose_translation
                        else:
                           values -= pose_translation

                        # add keyframes
                        for i, value in enumerate(values):
                            fps = bpy.context.scene.render.fps
                            frame = t * fps
                            translation_curves[i].keyframe_points.insert(frame, value)
                elif track['attr'] == 'rotation':
                    data_path = 'pose.bones["{0}"].rotation_quaternion'.format(track['name'])
                    quaternions = []
                    for t, value in track['keys']:
                        # manage root bone (quaternions in blender are WXYZ while heat uses XYZW)
                        if not armature.pose.bones[track['name']].parent:
                            quaternions.append([t,  armature.matrix_world.to_quaternion() @ pose[track['name']].to_quaternion().inverted() @ Quaternion((value[3], value[0], value[1], value[2]))])
                        else:
                            quaternions.append([t, pose[track['name']].to_quaternion().inverted() @ Quaternion((value[3], value[0], value[1], value[2]))])

                        # HACKY FIXES HERE (TODO: find better solutions)
                        # fix incorrect armature rotation when imported (the animation comes lying down by default)
                        if track['name'] == 'heat_Root':
                            quaternions[-1][1] = quaternions[-1][1] + Quaternion((0, -0.707107, 0, 0))
                        # fix inverted hips
                        if track['name'] == 'heat_Hips':
                            quaternions[-1][1] *= Quaternion((1, 1, -1, -1))
                        # fix inverted thumbs
                        if track['name'] == 'heat_Thumb1_l' or track['name'] == 'heat_Thumb1_r' :
                            quaternions[-1][1] *= Quaternion((1, 1, -1, -1))

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

            try:
                armature.animation_data.action = action
            finally:
                context.scene.heat_animation_id_downloading = False


    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
