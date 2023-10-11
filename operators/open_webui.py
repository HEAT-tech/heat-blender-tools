import bpy
import webbrowser

class OpenWebUIOperator(bpy.types.Operator):
    """Open Web UI in the default web browser"""
    bl_idname = "heat.open_web_ui"
    bl_label = "Open Web UI"

    def execute(self, context):
        url = "http://localhost:5000"
        webbrowser.open(url)
        return {'FINISHED'}