import bpy
from .. import custom_types, services
import os


class HeatToolsBrowserPanel(bpy.types.Panel):
    bl_idname = "HEAT_TOOLS_BROWSER_PT_panel"
    bl_label = "HeatTools Browser"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HeatTools"
    bl_order = 0


    def draw(self, context):
        layout = self.layout

        this_plugin_name = __name__.split(".")[0]
        heat_user_api_key = context.preferences.addons[this_plugin_name].preferences.heat_user_api_key
        if not heat_user_api_key:
            self.draw_auth(context, layout)
            return

        layout.label(text="Browse:")

        box = layout.box()
        box.row(align=True).prop(context.scene, 'heat_search_query', text='', icon='VIEWZOOM')
        # Expandable Advanced Search menu
        box.row(align=True).prop(context.scene, "heat_advanced_search", text="Filter Tags", icon="TRIA_DOWN" if context.scene.heat_advanced_search else "TRIA_RIGHT", emboss=False, icon_only=True, toggle=True)
        if context.scene.heat_advanced_search:
            box.row(align=True).label(text="Tags:")
            box.row(align=True).template_list(
                "HeatTagResultsList",
                "Heat_Tag_Results_List",
                context.scene,
                "heat_tag_results_list",
                context.scene,
                "heat_tag_results_list_index"
            )
            box.row(align=True).label(text="Movement Type:")
            box.row(align=True).prop(context.scene, "heat_motion_types")
        box.row(align=True).operator("heat.api_search_animations", text='Fetch Heat Animations', icon="FILE_REFRESH")
        layout.separator()

        layout.label(text="Results:")
        if context.scene.heat_animation_results_loading:
            results_box = layout.box()
            results_box.row(align=True).label(text="Fetching results...", icon="FILE_REFRESH")
        else:
            layout.template_list(
                "HeatAnimationResultsList",
                "Heat_Animation_Results_List",
                context.scene,
                "heat_animation_results_list",
                context.scene,
                "heat_animation_results_list_index"
            )
            self.draw_fetch_more(context, layout)
        layout.separator()

        self.draw_heat_animation_as_icon_preview(context, layout)

        if context.scene.heat_animation_id_downloading is not True:
            layout.operator("heat.download_animation", icon="IMPORT", text="Download")
        else:
            dl_loading_box = layout.box()
            dl_loading_box.separator()
            progress_bar = dl_loading_box.row()
            progress_bar.prop(bpy.context.scene,"heat_animation_id_downloading_progress", text="Downloading...")
            progress_lbl = dl_loading_box.row()
            progress_lbl.active = False
            progress_lbl.label(text="Press ESC to cancel")


    def draw_auth(self, context, layout):
        layout.label(text="YOU ARE NOT LOGGED IN!")
        layout.separator()
        layout.label(text="Please enter your API key")
        layout.label(text="in the addon's preferences")
        layout.separator()
        layout.label(text="You can find your API key")
        layout.label(text="in your account dashboard")
        layout.separator()
        layout.operator("heat.auth_get_api_key")
        layout.operator("screen.userpref_show")

    def draw_heat_animation_as_icon_preview(self, context, layout):
        layout.label(text="Preview:")
        preview_box = layout.box()

        if context.window_manager.heat_preview_webui:
            tpath = get_addon_thumbnail_path('heat_logo.png')
        elif context.scene.heat_animation_results_list_index >= 0:
            active_movement_index = context.scene.heat_animation_results_list_index
            active_movement = context.scene.heat_animation_results_list[active_movement_index]

            api = services.HeatAPIClient()
            image_name = f'zzz_heat_{active_movement.movement_id}.png'
            download_path = os.path.join(api.download_dir, image_name)
            self.clear_heat_anim_preview_image_blocks(image_name)

            if os.path.exists(download_path) == False:
                context.window_manager.heat_preview_texture_loading = True
                api.synchronous_download_file(active_movement.preview_image_url, download_path)

            # tpath = get_addon_thumbnail_path('dummy.png')
            tpath = download_path
        else:
            tpath = get_addon_thumbnail_path('heat_logo.png')

        img = bpy.data.images.load(tpath, check_existing=True)
        preview = img.preview_ensure()
        preview_box.template_icon(icon_value=preview.icon_id, scale=10.0)
        context.window_manager.heat_preview_texture_loading = False


    def draw_heat_animation_preview(self, context, layout):
        layout.label(text="Preview:")
        preview_box = layout.box()

        layout.operator("heat.create_preview_texture_operator")
        if context.scene.heat_preview_texture:
            texture = context.scene.heat_preview_texture
            preview_box.template_preview(texture.id_data)
            preview_box.label(text=f'Frames in preview: {texture.image.frame_duration}')
        else:
            texture = bpy.data.textures.new(name="HeatPreview", type="IMAGE")
            preview_box.template_preview(texture.id_data)


    def clear_heat_anim_preview_image_blocks(self, except_filename=''):
        # clear if the image name starts with "zzz_heat_" and it has no users
        # skips image with filename in except_filename
        for img in bpy.data.images:
            if img.name.startswith("zzz_heat_") and img.users == 0:
                if img.name == except_filename:
                    continue
                bpy.data.images.remove(img)

    def draw_fetch_more(self, context, layout):
        if context.scene.heat_animation_fetching_next_results_page:
            layout.box().row(align=True).label(text="Fetching...", icon="FILE_REFRESH")
            return
        if context.scene.heat_animation_next_results_page > 1:
            layout.operator('heat.api_fetch_more_animations', icon="FORWARD", text="More Results...")

    @classmethod
    def register(cls):
        bpy.utils.register_class(CreateHeatPreviewTextureOperator)

        bpy.types.Scene.heat_advanced_search = bpy.props.BoolProperty(default=False, update=handle_advanced_search_dropdown_change)
        bpy.types.Scene.heat_search_query = bpy.props.StringProperty(
            name="Search",
            default='',
            update=handle_search_query_change
        )
        bpy.types.Scene.heat_tag_results_list = bpy.props.CollectionProperty(
            type=custom_types.HeatTagResultListItem
        )
        bpy.types.Scene.heat_tag_results_list_index = bpy.props.IntProperty(
            name = "Index for Heat tag results",
            default = -1
        )
        bpy.types.Scene.heat_motion_types = bpy.props.EnumProperty(
            name="Motion Types",
            items=[
                ('hip', "Hip", "Hip Motion"),
                ('root', "Root", "Root Motion"),
                ('in_place', "In Place", "In Place Motion"),
            ],
            options={'ENUM_FLAG'}
        )

        bpy.types.Scene.heat_preview_texture = bpy.props.PointerProperty(type=bpy.types.Texture)
        bpy.types.WindowManager.heat_preview_texture_loading = bpy.props.BoolProperty(
            name = "Heat preview texture loading state",
            default = False
        )
        bpy.types.WindowManager.heat_preview_webui = bpy.props.BoolProperty(
            name = "Heat preview texture unavailable during webui use",
            default = False
        )

        bpy.types.Scene.heat_animation_results_loading = bpy.props.BoolProperty(
            name = "Heat animation results fetch state",
            default = False
        )
        bpy.types.Scene.heat_animation_id_downloading = bpy.props.BoolProperty(
            name = "Heat animation downloading state",
            default = False
        )
        bpy.types.Scene.heat_animation_id_downloading_progress = bpy.props.FloatProperty(
            name = "Heat animation downloading state",
            subtype="PERCENTAGE",
            soft_min=0,
            soft_max=100,
            precision=0,
        )
        bpy.types.Scene.heat_animation_results_list = bpy.props.CollectionProperty(
            type=custom_types.HeatAnimationResultListItem
        )
        bpy.types.Scene.heat_animation_results_list_index = bpy.props.IntProperty(
            name = "Index for Heat animation results",
            default = -1
        )
        bpy.types.Scene.heat_animation_next_results_page = bpy.props.IntProperty(
            name = "Next page index for Heat animation results",
            default = -1
        )
        bpy.types.Scene.heat_animation_fetching_next_results_page = bpy.props.BoolProperty(
            name = "Heat animation results fetching state",
            default = False
        )
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        bpy.utils.unregister_class(CreateHeatPreviewTextureOperator)
        del bpy.types.Scene.heat_advanced_search
        del bpy.types.Scene.heat_search_query
        del bpy.types.Scene.heat_motion_types
        del bpy.types.Scene.heat_preview_texture
        del bpy.types.WindowManager.heat_preview_texture_loading
        del bpy.types.WindowManager.heat_preview_webui
        del bpy.types.Scene.heat_animation_results_loading
        del bpy.types.Scene.heat_animation_id_downloading
        del bpy.types.Scene.heat_animation_id_downloading_progress
        del bpy.types.Scene.heat_animation_results_list
        del bpy.types.Scene.heat_animation_results_list_index
        del bpy.types.Scene.heat_animation_next_results_page
        del bpy.types.Scene.heat_animation_fetching_next_results_page
        print("Unregistered: %s" % cls.bl_label)


def get_addon_thumbnail_path(name):
    script_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(script_path, f"..{os.sep}assets")
    # fpath = os.path.join(p, subpath)
    ext = name.split('.')[-1]
    next = ''
    if not (ext == 'jpg' or ext == 'png' or ext == 'mp4'):  # already has ext?
        next = '.jpg'
    subpath = f"img{os.sep}{name}{next}"
    return os.path.join(script_path, subpath)

class CreateHeatPreviewTextureOperator(bpy.types.Operator):
    bl_idname = "heat.create_preview_texture_operator"
    bl_label = "Create Heat Preview Texture"

    def execute(self, context):
        # Create a new texture
        texture = bpy.data.textures.new(name="HeatPreview", type="IMAGE")

        # Set the texture properties
        image_path = get_addon_thumbnail_path('dance_dummy.mp4')
        image = bpy.data.images.load(image_path)
        texture.image = image
        texture.use_mipmap = True
        texture.use_interpolation = True
        texture.use_alpha = True

        texture.image_user.use_auto_refresh = True
        texture.image_user.use_cyclic = True
        texture.image_user.frame_current = 25

        context.scene.heat_preview_texture = texture

        return {'FINISHED'}

def handle_advanced_search_dropdown_change(self, context):
    if context.scene.heat_advanced_search:
        bpy.ops.heat.api_fetch_tags()

def handle_search_query_change(self, context):
    # print('wtf?')
    bpy.ops.heat.api_search_animations()