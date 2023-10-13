import bpy
import webbrowser
from .. import dotenv

class OpenWebUIOperator(bpy.types.Operator):
    """Open Web UI in the default web browser"""
    bl_idname = "heat.open_web_ui"
    bl_label = "Open Web UI"

    def execute(self, context):
        local_url = "http://localhost:5000"
        dev_url = "https://dev-blender.heat.tech"
        prod_url = "https://app-blender.heat.tech"

        env = dotenv.DotENV()
        url = prod_url
        if(env.is_true("HEAT_USE_DEV_API")):
            url = dev_url
        if(env.is_true("HEAT_USE_LOCAL_WEBUI")):
            url = local_url

        webbrowser.open(url)
        return {'FINISHED'}