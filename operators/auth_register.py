import bpy
import webbrowser

class AuthRegisterOperator(bpy.types.Operator):
    """Open a URL in the default web browser"""
    bl_idname = "heat.auth_register"
    bl_label = "Register an account"

    def execute(self, context):
        url = "https://heat.tech/coming-soon"
        webbrowser.open(url)
        return {'FINISHED'}

