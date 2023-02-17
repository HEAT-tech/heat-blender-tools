import os
import bpy


class BindWithAutoWeightsOperator(bpy.types.Operator):
    """Download Heat Animation"""
    bl_idname = "heat.bind_t69h_with_auto_weights"
    bl_label = "Bind to Mesh"
    bl_description = "Bind to Armature to Mesh with auto weights"

    def execute(self, context):
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        return {'FINISHED'}

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
