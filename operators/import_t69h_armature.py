import os
import bpy


class ImportT69HArmatureOperator(bpy.types.Operator):
    """Download Heat Animation"""
    bl_idname = "heat.import_t69h_armature"
    bl_label = "Import T69H Armature"

    def execute(self, context):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        t69h_glb_filepath = os.path.join(this_dir, '../t69h_v10.glb')
        bpy.ops.import_scene.gltf(filepath=t69h_glb_filepath)

        # remove mesh
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['T69H'].select_set(1)
        bpy.ops.object.delete()
        return {'FINISHED'}

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
