import bpy
import asyncio
import os
import json
from mathutils import Quaternion, Matrix, Vector
import gzip
# indicator libraries
import gpu
from gpu_extras.batch import batch_for_shader

from .. import services


class APIDownloadAnimationOperator(bpy.types.Operator):
    """Download Heat Animation"""
    bl_idname = "heat.download_animation"
    bl_label = "Download Heat Animation"

    # Variables for loading indicator
    width = 1.7
    height = 1.76
    x_pos = 0
    y_pos = 0
    download_progress = 0.0
    loading_progress = 0.0
    total_progress = 0.0
    loading = False
    view3d_area = None
    # asyncio task
    task = None

    def invoke(self, context, event):
        try:
            self.loading = True
            self.view3d_area = self.get_view3d_area(context)

            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                self.draw, (context,),
                'WINDOW', 'POST_VIEW')

            context.window_manager.modal_handler_add(self)

            # set loading indicator location
            armature = self.get_active_armature()
            if armature:
                self.x_pos = armature.location.x
                self.y_pos = armature.location.y

            # download animation
            self.task = asyncio.ensure_future(self.download_file(context))
            services.ensure_async_loop()
            context.area.tag_redraw()
        except:
            self.loading = False
            context.scene.heat_animation_id_downloading = False
            print('Error occurred while downloading...')
            raise RuntimeError('Error occurred while downloading...')

        if not self.loading:
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        self.view3d_area.tag_redraw()
        self.total_progress = (self.download_progress * 0.9) + (self.loading_progress * 0.1)
        context.scene.heat_animation_id_downloading_progress = self.total_progress * 100
        self.report_status(context)

        if event.type == 'ESC':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            if self.task:
                self.task.cancel()
            self.loading = False
            context.scene.heat_animation_id_downloading = False
            return {'CANCELLED'}

        # Check if aiohttp request is finished
        if not self.loading:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    async def download_file(self, context):
        api = services.HeatAPIClient()

        active_movement_index = context.scene.heat_animation_results_list_index
        active_movement = context.scene.heat_animation_results_list[active_movement_index]
        download_path = os.path.join(api.download_dir, 'animation.heat')

        # download file from heat
        context.scene.heat_animation_id_downloading = True
        await api.download_file(active_movement.download_url, download_path, self)
        self.loading_progress = 0.1

        # import T69H and/or apply animation fcurves from response
        active_object = bpy.context.active_object
        armature = bpy.context.scene.objects.find('Armature')

        if active_object is not None:
            if active_object.type == 'ARMATURE':
                armature = active_object
            elif active_object.parent is None:
                bpy.ops.heat.import_t69h()
                armature = bpy.context.scene.objects['Armature']
            elif active_object.parent.type == 'ARMATURE':
                armature = active_object.parent
        elif armature >= 0:
            armature = bpy.context.scene.objects['Armature']
        elif armature == -1:
            bpy.ops.heat.import_t69h()
            armature = bpy.context.scene.objects['Armature']

        if armature.animation_data is None:
            armature.animation_data_create()

        self.loading_progress = 0.5
        # apply animation to armature as a new action
        with gzip.open(download_path, 'rb') as f:
            data = json.load(f)
            action_name = 'heat_"{0}"'.format(active_movement.name)
            action = bpy.data.actions.new(action_name)

            pose = {}
            def fill_pose(pose, joint):
                m = joint['local_matrix']
                # blender is row major
                pose[joint['name']] = Matrix([m[0:4], m[4:8], m[8:12], m[12:16]]).transposed()
                for child in joint['children']:
                    fill_pose(pose, child)

            fill_pose(pose, data['pose'])

            total_tracks = len(data['tracks'])
            current_track = 0
            for track in data['tracks']:
                current_track += 1
                self.loading_progress += (current_track / total_tracks) * 0.5

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
                           #  root bone
                           values -= armature.matrix_world.to_translation() - pose_translation
                        else:
                           intended_location = values - pose_translation
                           pose_bone = armature.pose.bones[track['name']]
                           # determine final local location based on global location
                           taxi = intended_location + pose_bone.bone.matrix_local.to_translation()
                           # pray
                           values = pose_bone.bone.matrix_local.inverted() @ taxi * Vector((1, -1, -1))

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

                        # negate quaternion if quaternion is all negatives
                        if all(q < 0 for q in quaternions[-1][1]):
                            quaternions[-1][1] *= -1
                        # negate quaternion if W is negative
                        if quaternions[-1][1][0] < 0 and track['name'] != 'heat_Root':
                            quaternions[-1][1] *= -1

                        # HACKY FIXES HERE (TODO: find better solutions)
                        # fix incorrect armature rotation when imported (the animation comes lying down by default)
                        if track['name'] == 'heat_Root':
                            # quaternions[-1][1] = quaternions[-1][1] + Quaternion((0, -0.707107, 0, 0))
                            quaternions[-1][1] = Quaternion((1, 0, 0, 0))
                        # fix inverted hips
                        if track['name'] == 'heat_Hips':
                            quaternions[-1][1] *= Quaternion((1, 1, -1, -1))
                        # fix inverted thumbs
                        if track['name'] == 'heat_Thumb1_r':
                            quaternions[-1][1] *= Quaternion((1, 1, -1, -1))
                        if track['name'] == 'heat_Thumb1_l' :
                            q = Quaternion((quaternions[-1][1][0], quaternions[-1][1][3], quaternions[-1][1][1], quaternions[-1][1][2]))
                            quaternions[-1][1] = q * Quaternion((1, 1, 1, 1))

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
                self.loading_progress = 0.9
                armature.animation_data.action = action
            finally:
                self.loading_progress = 1.0
                context.scene.heat_animation_id_downloading = False
                self.loading = False

    # Create Wireframe Cube Vertices and Edges
    def create_wireframe_cube_vertices(self, width, height, x_pos=0, y_pos=0):
        width = width/2
        vertices = [
            (x_pos+(-width), y_pos+(-width), 0),
            (x_pos+width, y_pos+(-width), 0),
            (x_pos+width, y_pos+width, 0),
            (x_pos+(-width), y_pos+width, 0),
            (x_pos+(-width), y_pos+(-width), height),
            (x_pos+width, y_pos+(-width), height),
            (x_pos+width, y_pos+width, height),
            (x_pos+(-width), y_pos+width, height)
        ]
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        return vertices, edges

    # Create Inner Cube Vertices
    def create_inner_cube_vertices(self, width, height, x_pos=0, y_pos=0):
        height = height * self.total_progress
        width = width / 2
        return (
        # bottom face
            (x_pos+(-width), y_pos+width, 0), (x_pos+width, y_pos+width, 0), (x_pos+width, y_pos+(-width), 0),
            (x_pos+(-width), y_pos+width, 0), (x_pos+width, y_pos+(-width), 0), (x_pos+(-width), y_pos+(-width), 0),
        # top face
            (x_pos+(-width), y_pos+width, height), (x_pos+width, y_pos+width, height), (x_pos+width, y_pos+(-width), height),
            (x_pos+(-width), y_pos+width, height), (x_pos+width, y_pos+(-width), height), (x_pos+(-width), y_pos+(-width), height),
        # -x face
            (x_pos+(-width), y_pos+width, height), (x_pos+(-width), y_pos+(-width), height), (x_pos+(-width), y_pos+(-width), 0),
            (x_pos+(-width), y_pos+width, height), (x_pos+(-width), y_pos+width, 0), (x_pos+(-width), y_pos+(-width), 0),
        # +x face
            (x_pos+width, y_pos+width, height), (x_pos+width, y_pos+(-width), height), (x_pos+width, y_pos+(-width), 0),
            (x_pos+width, y_pos+width, height), (x_pos+width, y_pos+width, 0), (x_pos+width, y_pos+(-width), 0),
        # -y face
            (x_pos+width, y_pos+(-width), height), (x_pos+(-width), y_pos+(-width), height), (x_pos+(-width), y_pos+(-width), 0),
            (x_pos+width, y_pos+(-width), height), (x_pos+width, y_pos+(-width), 0), (x_pos+(-width), y_pos+(-width), 0),
        # +y face
            (x_pos+width, y_pos+width, height), (x_pos+(-width), y_pos+width, height), (x_pos+(-width), y_pos+width, 0),
            (x_pos+width, y_pos+width, height), (x_pos+width, y_pos+width, 0), (x_pos+(-width), y_pos+width, 0),
        )


    # Draw function
    def draw(self, context):
        # Inner Cube
        inner_vertices = self.create_inner_cube_vertices(self.width, self.height, self.x_pos, self.y_pos)
        inner_shader = gpu.shader.from_builtin('3D_SMOOTH_COLOR')
        inner_batch = batch_for_shader(inner_shader, 'TRIS', {"pos": inner_vertices, "color": [(1, 0, 0, 0.5)] * len(inner_vertices)})

        # Wireframe Cube
        wireframe_vertices, wireframe_edges = self.create_wireframe_cube_vertices(self.width, self.height, self.x_pos, self.y_pos)
        wireframe_shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        wireframe_batch = batch_for_shader(wireframe_shader, 'LINES', {"pos": wireframe_vertices}, indices=wireframe_edges)

        # Draw Inner Cube
        inner_shader.bind()
        inner_batch.draw(inner_shader)

        # Draw Wireframe Cube
        wireframe_shader.bind()
        wireframe_shader.uniform_float("color", (1, 1, 1, 1))
        wireframe_batch.draw(wireframe_shader)

    def report_status(self, context):
        progress = int(self.total_progress * 100)
        message = f"Loading ({progress}%). Press ESC to cancel."

        # Display a message in the status bar
        context.workspace.status_text_set(text=message)

        if self.total_progress == 1:
            self.report({"INFO"}, "Loading completed.")

    def get_view3d_area(self, context):
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                return area
        return None

    def get_active_armature(self):
        active_object = bpy.context.active_object
        armature = bpy.context.scene.objects.find('Armature')

        if active_object is not None:
            if active_object.type == 'ARMATURE':
                return active_object
            elif active_object.parent.type == 'ARMATURE':
                return active_object.parent
        elif armature >= 0:
            return bpy.context.scene.objects['Armature']
        return None


    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)