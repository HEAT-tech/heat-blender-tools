import bpy


class UniformScaleArmatureOperator(bpy.types.Operator):
    bl_idname = "object.uniform_scale_armature"
    bl_label = "Uniform Scale Armature"

    def execute(self, context):
        armature = bpy.data.objects['Armature']

        # Clear any f-curves animating the armature scale
        action = armature.animation_data.action
        for fc in [*action.fcurves]:
            if fc.data_path == "scale":
                action.fcurves.remove(fc)

        armature.scale = (0.01, 0.01, 0.01)
        return {'FINISHED'}
