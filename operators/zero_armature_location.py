import bpy


class ZeroArmatureLocationOperator(bpy.types.Operator):
    bl_idname = "object.zero_armature_location"
    bl_label = "Zero Armature Location"

    def execute(self, context):
        armature = bpy.data.objects['Armature']

        # Clear any f-curves animating the armature location
        action = armature.animation_data.action
        for fc in [*action.fcurves]:
            if fc.data_path == "location":
                action.fcurves.remove(fc)

        armature.location = (0.0, 0.0, 0.0)
        return {'FINISHED'}

