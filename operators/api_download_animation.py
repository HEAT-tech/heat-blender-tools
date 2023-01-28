import bpy
import asyncio

from .. import services


class APIDownloadAnimationOperator(bpy.types.Operator):
    """Download Heat Animation"""
    bl_idname = "heat.download_animation"
    bl_label = "Download Heat Animation"

    def execute(self, context):
        async_task = asyncio.ensure_future(self.get_movements())
        services.ensure_async_loop()
        return {'FINISHED'}

    async def get_movements(self):
        api = services.HeatAPIClient()
        await api.get_movements()

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
