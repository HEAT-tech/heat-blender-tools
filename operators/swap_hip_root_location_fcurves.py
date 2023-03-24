import bpy
from mathutils import Vector

class SwapHipsRootLocationFCurvesOperator(bpy.types.Operator):
    """Swap the hip and root location fcurves so armature is animated via root"""
    bl_label = "Convert to Root Control"
    bl_idname = "heat.swap_hips_root_location_fcurves"

    def execute(self, context):
        active_object = bpy.context.active_object
        armature =  bpy.context.scene.objects.find('Armature')

        if active_object is not None:
            if active_object.type == 'ARMATURE':
                armature = active_object
            elif active_object.parent.type == 'ARMATURE':
                armature = active_object.parent
        elif armature >= 0:
            armature = bpy.context.scene.objects['Armature']

        root_x = armature.animation_data.action.fcurves.find('pose.bones["heat_Root"].location', index=0)
        root_y = armature.animation_data.action.fcurves.find('pose.bones["heat_Root"].location', index=1)
        root_z = armature.animation_data.action.fcurves.find('pose.bones["heat_Root"].location', index=2)

        hips_x = armature.animation_data.action.fcurves.find('pose.bones["heat_Hips"].location', index=0)
        hips_y = armature.animation_data.action.fcurves.find('pose.bones["heat_Hips"].location', index=1)
        hips_z = armature.animation_data.action.fcurves.find('pose.bones["heat_Hips"].location', index=2)


        for i in range(len(root_x.keyframe_points)):
            root_x.keyframe_points.remove(root_x.keyframe_points[0])
        for i in range(len(root_y.keyframe_points)):
            root_y.keyframe_points.remove(root_y.keyframe_points[0])
        for i in range(len(root_z.keyframe_points)):
            root_z.keyframe_points.remove(root_z.keyframe_points[0])


        keyframes = []
        for i in range(len(hips_x.keyframe_points)):
            frame = hips_x.keyframe_points[i].co[0]
            value = Vector((
                hips_x.keyframe_points[i].co[1],
                hips_y.keyframe_points[i].co[1],
                hips_z.keyframe_points[i].co[1]
            ))
            keyframes.append((frame, value))

        # rest hip to starting position before processing
        armature.pose.bones['heat_Hips'].location = keyframes[0][1]
        zero_pos_y = 0

        for i in range(len(keyframes)):
            frame = keyframes[i][0]
            hb_location = keyframes[i][1]
            pose_bone = armature.pose.bones['heat_Hips']
            rb_location = armature.matrix_world @ pose_bone.bone.matrix_local @ hb_location * Vector((100, -100, 100))
            if i == 0:
                zero_pos_y = rb_location[2]

            root_x.keyframe_points.insert(frame, rb_location[0])
            root_y.keyframe_points.insert(frame, rb_location[2] - zero_pos_y)
            root_z.keyframe_points.insert(frame, rb_location[1])

        armature.animation_data.action.fcurves.remove(hips_x)
        armature.animation_data.action.fcurves.remove(hips_y)
        armature.animation_data.action.fcurves.remove(hips_z)
        return {'FINISHED'}
