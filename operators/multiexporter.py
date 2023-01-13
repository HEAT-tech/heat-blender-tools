import bpy


class MultiexporterOperator(bpy.types.Operator):
    """Click to select directory to export to and export"""
    bl_idname = "scene.heat_multiexporter"
    bl_label = "Multiexporter"

    directory: bpy.props.StringProperty(name="Directory")
    filename: bpy.props.StringProperty(name="File Name")
    filepath: bpy.props.StringProperty(name="File Path")

    def execute(self, context):
        export_fbx = context.scene.heat_multiexporter_export_fbx
        if export_fbx:
            bpy.ops.export_scene.fbx(filepath=self.filepath+'.fbx', add_leaf_bones=False)

        export_gltf = context.scene.heat_multiexporter_export_gltf
        if export_gltf:
            bpy.ops.export_scene.gltf(filepath=self.filepath)

        return {'FINISHED'}


    def invoke(self, context, event):
        # Open browser, take reference to 'self' read the path to selected
        # file, put path in predetermined self fields.
        # See: https://docs.blender.org/api/current/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
        context.window_manager.fileselect_add(self)
        # Tells Blender to hang on for the slow user input
        return {'RUNNING_MODAL'}

    @classmethod
    def register(cls):
        bpy.types.Scene.heat_multiexporter_export_fbx = bpy.props.BoolProperty (
            name="Export FBX",
            description="Export FBX",
        )
        bpy.types.Scene.heat_multiexporter_export_gltf = bpy.props.BoolProperty (
            name="Export GLTF",
            description="Export GLTF",
        )
        bpy.types.Scene.heat_multiexporter_upload_to_heat = bpy.props.BoolProperty (
            name="Upload to Heat",
            description="Upload to Heat",
        )
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.heat_multiexporter_export_fbx
        del bpy.types.Scene.heat_multiexporter_export_gltf
        del bpy.types.Scene.heat_multiexporter_upload_to_heat
        print("Unregistered: %s" % cls.bl_label)
