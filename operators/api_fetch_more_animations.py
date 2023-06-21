import bpy
import asyncio
from .. import services


class APIFetchMoreAnimationsOperator(bpy.types.Operator):
    bl_idname = "heat.api_fetch_more_animations"
    bl_label = "Fetch More Heat Animations"

    def execute(self, context):
        async_task = asyncio.ensure_future(self.get_movements(context))
        services.ensure_async_loop()

        return {'FINISHED'}


    async def get_movements(self, context):
        api = services.HeatAPIClient()
        context.scene.heat_animation_fetching_next_results_page = True

        params = services.build_params_list_from_scene_params()
        next_page = context.scene.heat_animation_next_results_page
        if next_page <= 0:
            return
        params['page'] = next_page

        try:
            movements = await api.get_movements(2, params)
            services.add_movements_to_results_list(movements)
        except:
            def error(self, context):
                self.layout.label(text="Please make sure your HEAT API key is correct")
                self.layout.label(text="and that you have a stable internet connection.")
            bpy.context.window_manager.popup_menu(error, title="ERROR FETCHING ANIMATIONS", icon='ERROR')


        context.scene.heat_animation_fetching_next_results_page = False
        context.area.tag_redraw()

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
