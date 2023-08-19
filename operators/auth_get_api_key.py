import bpy
import webbrowser

class AuthGetAPIKeyOperator(bpy.types.Operator):
    """Open a URL in the default web browser"""
    bl_idname = "heat.auth_get_api_key"
    bl_label = "Get API Key"

    def execute(self, context):
        url = "https://heat.tech/dashboard/account"
        webbrowser.open(url)
        return {'FINISHED'}