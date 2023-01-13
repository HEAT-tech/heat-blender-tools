import bpy


class HeatToolsBatchPanel(bpy.types.Panel):
    bl_idname = "HEAT_TOOLS_BATCH_PT_panel"
    bl_label = "HeatTools Batch"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HeatTools"
    bl_order = 1

    def draw(self, context):
        layout = self.layout
        layout.label(text="HEAT TOOLS BATCH", icon='COLORSET_01_VEC')
        layout.separator()


        box = layout.box()
        box.label(text="Import directory:")
        row = box.row()
        row.prop(context.scene, 'heat_import_directory_prop', text="")
        row.operator("heat.import_dir", icon='FILE_FOLDER', text="")
        box.separator()

        box.label(text="Export directory:")
        row = box.row()
        row.prop(context.scene, 'heat_export_directory_prop', text="")
        row.operator("heat.export_dir", icon='FILE_FOLDER', text="")
        box.prop(context.scene, 'heat_export_use_lookin_directory_prop', text="Use look-in directory")
        box.separator()

        layout.label(text="Batch settings:")
        layout.prop(context.scene, 'heat_multiexporter_export_fbx')
        layout.prop(context.scene, 'heat_multiexporter_export_gltf')
        layout.prop(context.scene, 'heat_multiexporter_upload_to_heat')
        layout.operator("heat.process_batch")

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)