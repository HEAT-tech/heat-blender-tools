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
        params = {}

        # build params list
        if context.scene.heat_search_query != '':
            params['q'] = context.scene.heat_search_query
        motion_type_set = context.scene.heat_motion_types
        motion_types = ','.join([str(m_type) for m_type in motion_type_set])
        if motion_types!= '':
            params['motionTypes'] = motion_types
        selected_tags = _get_selected_tags()
        if len(selected_tags):
            params['tags'] = ','.join([str(tag.id) for tag in selected_tags])

        # try:
        movements = await api.get_movements(2, params)
        for movement in movements:
            new_movement = context.scene.heat_animation_results_list.add()
            new_movement.name = movement['name']
            new_movement.movement_id = movement['id']
            new_movement.description = movement['description']
            new_movement.download_url = movement['downloadUrl']
            new_movement.preview_image_url = movement['previewImageUrl']
            new_movement.url = movement['url']

            if not movement['tags']:
                continue
            for tag in movement['tags']:
                tag_item = new_movement.tags.add()
                tag_item['id'] = tag['id']
                tag_item['url'] = tag['url']
                tag_item['parent_id'] = tag['parentID'] or -1
                tag_item['name'] = tag['name']

        # except:
        #     def error(self, context):
        #         self.layout.label(text="Please make sure your HEAT API key is correct")
        #         self.layout.label(text="and that you have a stable internet connection.")
        #     bpy.context.window_manager.popup_menu(error, title="ERROR FETCHING ANIMATIONS", icon='ERROR')


        context.scene.heat_animation_results_loading = False
        context.area.tag_redraw()

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
