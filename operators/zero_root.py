import bpy
import mathutils


class ZeroRootOperator(bpy.types.Operator):
    bl_idname = "object.zero_root"
    bl_label = "Zero Root"

    def execute(self, context):
        context.scene.frame_set(1)

        # Get the object
        armature = bpy.data.objects["Armature"]
        bone = armature.pose.bones["CC_Base_Hip"]

        # Get required offset
        inv_bone_location = bone.location * -1

        # Get the animation data
        fcs = armature.animation_data.action.fcurves
        # Get xyz fcurve data for CC_Base_Hip bone
        cc_base_hip_x_fc = fcs.find('pose.bones["CC_Base_Hip"].location', index=0)
        cc_base_hip_y_fc = fcs.find('pose.bones["CC_Base_Hip"].location', index=1)
        cc_base_hip_z_fc = fcs.find('pose.bones["CC_Base_Hip"].location', index=2)

        # Loop through each "CC_Base_Hip" location fcurve and zero the location
        for kf in cc_base_hip_x_fc.keyframe_points:
            kf.co += mathutils.Vector((0.0, inv_bone_location.x))

        for kf in cc_base_hip_y_fc.keyframe_points:
            kf.co += mathutils.Vector((0.0, inv_bone_location.y))

        for kf in cc_base_hip_z_fc.keyframe_points:
            kf.co += mathutils.Vector((0.0, inv_bone_location.z))

        return {'FINISHED'}

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
