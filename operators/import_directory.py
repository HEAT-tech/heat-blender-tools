import bpy

class ImportDirOperator(bpy.types.Operator):
    """Select directory to import for batch processing"""
    bl_idname = "heat.import_dir"
    bl_label = "Select a Directory"
    bl_options = {'REGISTER'}

    # Define this to tell 'fileselect_add' that we want a directory
    directory: bpy.props.StringProperty(name="Directory")
    # filter_folder: bpy.props.BoolProperty(default=True, options={'HIDDEN'})

    def execute(self, context):
        context.scene.heat_import_directory_prop = self.directory
        print("Selected dir: '" + self.directory + "'")
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
        bpy.types.Scene.heat_import_directory_prop = bpy.props.StringProperty (
            name="Import Directory",
            description="Directory to import for batch processing",
            default=""
        )
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.heat_import_directory_prop
        print("Unregistered: %s" % cls.bl_label)
