import bpy
from .select_directory import SelectDirOperator

class ExportOperator(SelectDirOperator):
    """Select directory to export batch processing"""
    bl_idname = "heat.export_dir"
    bl_label = "Export"

    def draw(self, context):
        layout = self.layout
        layout.label(text="HEAT TOOLS BATCH", icon='COLORSET_01_VEC')
        layout.label(text="Select a directory to export batch processed files")

    def execute(self, context):
        context.scene.heat_export_directory_prop = self.directory
        return {'FINISHED'}

    @classmethod
    def register(cls):
        bpy.types.Scene.heat_export_directory_prop = bpy.props.StringProperty (
            name="Export Directory",
            description="Directory to export for batch processing",
            default=""
        )
        bpy.types.Scene.heat_export_use_lookin_directory_prop = bpy.props.BoolProperty (
            name="Use Look-in as export Directory",
            description="Directory to export for batch processing",
        )
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.heat_export_directory_prop
        del bpy.types.Scene.heat_export_use_lookin_directory_prop
        print("Unregistered: %s" % cls.bl_label)