import bpy


class HeatToolsPanel(bpy.types.Panel):
    bl_idname = "HEAT_TOOLS_PT_panel"
    bl_label = "HeatTools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HeatTools"
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="HEAT TOOLS V1", icon='COLORSET_02_VEC')
        layout.separator()

        arm_tools_box = layout.box()
        arm_tools_box.label(text="Armature Tools")
        arm_tools_box.operator("object.uniform_scale_armature")
        arm_tools_box.operator("object.zero_armature_location")
        arm_tools_box.operator("object.zero_root", text="Zero Root")
        layout.separator()

        bone_tools_box = layout.box()
        bone_tools_box.label(text="Bone Renamer")
        bone_tools_box.prop(context.scene, 'rename_bones_from')
        bone_tools_box.prop(context.scene, 'rename_bones_to')
        bone_tools_box.operator("object.rename_bones")
        layout.separator()

        multiexporter_box = layout.box()
        multiexporter_box.label(text="Multiexporter")
        multiexporter_box.prop(context.scene, 'heat_multiexporter_export_fbx')
        multiexporter_box.prop(context.scene, 'heat_multiexporter_export_gltf')
        multiexporter_box.prop(context.scene, 'heat_multiexporter_upload_to_heat')
        multiexporter_box.operator("scene.heat_multiexporter", text="Export")

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)