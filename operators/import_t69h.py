import os
import bpy


class ImportT69HOperator(bpy.types.Operator):
    """Download Heat Animation"""
    bl_idname = "heat.import_t69h"
    bl_label = "Import T69H Armature/Model"

    def execute(self, context):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        t69h_glb_filepath = os.path.join(this_dir, '../T69H_v12.glb')
        bpy.ops.import_scene.gltf(filepath=t69h_glb_filepath)
        return {'FINISHED'}

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
