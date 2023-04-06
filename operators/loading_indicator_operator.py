import blf
import bpy
import asyncio
import aiohttp
import bpy_extras


def draw_callback_px(self, context):
    pos3d = bpy.context.scene.cursor.location
    pos2d = bpy_extras.object_utils.world_to_camera_view(context.scene, context.scene.camera, pos3d)
    if (0.0 <= pos2d.x <= 1.0) and (0.0 <= pos2d.y <= 1.0):
        x, y = bpy.context.region.width * pos2d.x, bpy.context.region.height * pos2d.y
        size = 50
        stroke = 2
        color = (1.0, 1.0, 1.0, 1.0)
        blf.size(0, size, 72)
        blf.color(0, *color)
        blf.position(0, x - size / 2, y - size / 2, 0)
        blf.dimensions(0, size, size)
        blf.draw_circle(0, 0, 0.5 - stroke, 0.5 + stroke, 128)


class LoadingIndicatorOperator(bpy.types.Operator):
    bl_idname = "object.loading_indicator_operator"
    bl_label = "Loading Indicator Operator"

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def load_data(self, url):
        async with aiohttp.ClientSession() as session:
            html = await self.fetch(session, url)
            self.loading = False
            # Do something with the loaded data

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'ESC':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        # Draw loading indicator
        # self._handle()

        # Check if aiohttp request is finished
        if not self.loading:
            return {'FINISHED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.loading = True
        self._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_callback_px, (self, context,),
            'WINDOW', 'POST_PIXEL')

        asyncio.ensure_future(self.load_data('https://google.com'))

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw_callback_px(self, context):
        if self.loading:
            pos3d = bpy.context.scene.cursor.location
            pos2d = bpy_extras.object_utils.world_to_camera_view(context.scene, context.scene.camera, pos3d)
            if (0.0 <= pos2d.x <= 1.0) and (0.0 <= pos2d.y <= 1.0):
                x, y = bpy.context.region.width * pos2d.x, bpy.context.region.height * pos2d.y
                size = 50
                stroke = 2
                color = (1.0, 1.0, 1.0, 1.0)
                blf.size(0, size, 72)
                blf.color(0, *color)
                blf.position(0, x - size / 2, y - size / 2, 0)
                blf.dimensions(0, size, size)
                blf.draw_circle(0, 0, 0.5 - stroke, 0.5 + stroke, 128)

    def execute(self, context):
        return {'FINISHED'}
