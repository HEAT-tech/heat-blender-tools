import os
import bpy


class ImportT69HArmatureOperator(bpy.types.Operator):
    """T69H Armature"""
    bl_idname = "heat.import_t69h_armature"
    bl_label = "T69H Armature"
    bl_description = "T69H Armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        t69h_glb_filepath = os.path.join(this_dir, '../ t69h_v20_armature_only.glb')
        bpy.ops.import_scene.gltf(filepath=t69h_glb_filepath, bone_heuristic='TEMPERANCE')
        return {'FINISHED'}

    def menu_func(self, context):
        self.layout.operator(ImportT69HArmatureOperator.bl_idname, icon="ARMATURE_DATA")

    @classmethod
    def register(cls):
        bpy.types.VIEW3D_MT_armature_add.append(cls.menu_func)
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        bpy.types.VIEW3D_MT_armature_add.remove(cls.menu_func)
        print("Unregistered: %s" % cls.bl_label)
