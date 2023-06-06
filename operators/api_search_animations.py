import bpy
import asyncio
from .. import services

class APISearchAnimationsOperator(bpy.types.Operator):
    bl_idname = "heat.api_search_animations"
    bl_label = "Search Heat Animations"

    def execute(self, context):
        context.scene.heat_animation_results_list.clear()
        async_task = asyncio.ensure_future(self.get_movements(context))
        services.ensure_async_loop()

        return {'FINISHED'}


    async def get_movements(self, context):
        api = services.HeatAPIClient()
        context.scene.heat_animation_results_loading = True

        try:
            movements = await api.get_movements()
            for movement in movements:
                new_movement = context.scene.heat_animation_results_list.add()
                new_movement.name = movement['name']
                new_movement.movement_id = movement['movementID']
                new_movement.description = movement['description']
                new_movement.download_url = movement['downloadUrl']
                new_movement.preview_image_url = movement['previewImageUrl']
                new_movement.url = movement['url']
        except:
            def error(self, context):
                self.layout.label(text="Please make sure your HEAT API key is correct")
                self.layout.label(text="and that you have a stable internet connection.")
            bpy.context.window_manager.popup_menu(error, title="ERROR FETCHING ANIMATIONS", icon='ERROR')


        context.scene.heat_animation_results_loading = False
        context.area.tag_redraw()


    @classmethod
    def register(cls):
        bpy.types.Scene.heat_search_query = bpy.props.StringProperty(default="")
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.heat_search_query
        print("Unregistered: %s" % cls.bl_label)
