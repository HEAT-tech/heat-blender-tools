import bpy
import asyncio
from .. import services

class APISearchAnimationsOperator(bpy.types.Operator):
    bl_idname = "heat.api_search_animations"
    bl_label = "Search Heat animations"

    def execute(self, context):
        context.scene.heat_animation_results_list.clear()
        async_task = asyncio.ensure_future(self.get_movements(context))
        services.ensure_async_loop()

        return {'FINISHED'}


    async def get_movements(self, context):
        api = services.HeatAPIClient()
        context.scene.heat_animation_results_loading = True

        movements = await api.get_movements()
        for movement in movements:
            new_movement = context.scene.heat_animation_results_list.add()
            new_movement.name = movement['name']
            new_movement.id = movement['movementID']
            new_movement.description = movement['description']
            new_movement.download_url = movement['downloadUrl']
            new_movement.url = movement['url']

        context.scene.heat_animation_results_loading = False


    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
