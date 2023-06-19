import bpy
import asyncio
from .. import services

class APIFetchTagsOperator(bpy.types.Operator):
    bl_idname = "heat.api_fetch_tags"
    bl_label = "Fetch Heat Tags"

    def execute(self, context):
        async_task = asyncio.ensure_future(self.get_tags(context))
        services.ensure_async_loop()

        return {'FINISHED'}


    async def get_tags(self, context):
        api = services.HeatAPIClient()

        try:
            tags = await api.get_movement_tags()
            context.scene.heat_tag_results_list.clear()
            for tag in tags:
                new_tag = context.scene.heat_tag_results_list.add()
                new_tag.id = tag['id']
                new_tag.parent_id = tag['parentID'] or -1
                new_tag.name = tag['name']
                new_tag.url = tag['url']
        except:
            def error(self, context):
                self.layout.label(text="Please make sure your HEAT API key is correct")
                self.layout.label(text="and that you have a stable internet connection.")
            bpy.context.window_manager.popup_menu(error, title="ERROR FETCHING TAGS", icon='ERROR')

        bpy.ops.heat.panic_reset()


    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
