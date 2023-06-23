import bpy
import asyncio
from .. import services


def _get_selected_tags():
    tags = bpy.context.scene.heat_tag_results_list
    return [tag for tag in tags if tag.selected]


class APISearchAnimationsOperator(bpy.types.Operator):
    bl_idname = "heat.api_search_animations"
    bl_label = "Search Heat Animations"

    def execute(self, context):
        context.scene.heat_animation_results_list_index = -1
        context.scene.heat_animation_results_list.clear()
        async_task = asyncio.ensure_future(self.get_movements(context))
        services.ensure_async_loop()

        return {'FINISHED'}


    async def get_movements(self, context):
        api = services.HeatAPIClient()
        context.scene.heat_animation_results_loading = True
        params = services.build_params_list_from_scene_params()

        try:
            movements = await api.get_movements(2, params)
            services.add_movements_to_results_list(movements)
        except:
            def error(self, context):
                self.layout.label(text="Please make sure your HEAT API key is correct")
                self.layout.label(text="and that you have a stable internet connection.")
            bpy.context.window_manager.popup_menu(error, title="ERROR FETCHING ANIMATIONS", icon='ERROR')


        context.scene.heat_animation_results_loading = False
        context.area.tag_redraw()

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
