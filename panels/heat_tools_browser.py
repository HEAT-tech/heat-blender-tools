import bpy
from .. import custom_types
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

        layout.label(text="Browse HEAT Animations")
        layout.separator()

        # layout.prop(context.scene, "heat_search_query", text='')
        layout.operator("heat.api_search_animations", text='Fetch Heat Animations', icon="FILE_REFRESH")
        layout.separator()

        layout.label(text="Results:")
        if context.scene.heat_animation_results_loading:
            layout.label(text="Fetching results...")
        else:
            layout.template_list(
                "HeatAnimationResultsList",
                "Heat_Animation_Results_List",
                context.scene,
                "heat_animation_results_list",
                context.scene,
                "heat_animation_results_list_index"
            )
        layout.separator()

        self.draw_heat_animation_as_icon_preview(context, layout)

        if context.scene.heat_animation_id_downloading is not True:
            layout.operator("heat.download_animation", icon="IMPORT", text="Download")
        else:
            dl_loading_box = layout.box()
            dl_loading_box.label(text="Downloading...", icon="SORTTIME")
        layout.separator()

        layout.label(text="Armature actions:")
        layout.operator("heat.import_t69h_armature", text="Import New Armature")
        layout.operator("heat.import_t69h", text="Import Armature+Mesh")
        layout.operator("heat.bind_t69h_with_auto_weights")


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
        if context.scene.heat_animation_results_list_index >= 0:
            tpath = get_addon_thumbnail_path('dummy.png')
        else:
            tpath = get_addon_thumbnail_path('heat.png')

        img = bpy.data.images.load(tpath, check_existing = True)
        preview = img.preview_ensure()
        preview_box.template_icon(icon_value=preview.icon_id, scale=10.0)


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


    @classmethod
    def register(cls):
        bpy.utils.register_class(CreateHeatPreviewTextureOperator)
        bpy.types.Scene.heat_preview_texture = bpy.props.PointerProperty(type=bpy.types.Texture)

        bpy.types.Scene.heat_animation_results_loading = bpy.props.BoolProperty(
            name = "Heat animation results fetch state",
            default = False
        )
        bpy.types.Scene.heat_animation_id_downloading = bpy.props.BoolProperty(
            name = "Heat animation downloading state",
            default = False
        )
        bpy.types.Scene.heat_animation_results_list = bpy.props.CollectionProperty(
            type=custom_types.HeatAnimationResultListItem
        )
        bpy.types.Scene.heat_animation_results_list_index = bpy.props.IntProperty(
            name = "Index for Heat animation results",
            default = -1
        )
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        bpy.utils.unregister_class(CreateHeatPreviewTextureOperator)
        del bpy.types.Scene.heat_preview_texture
        del bpy.types.Scene.heat_animation_results_loading
        del bpy.types.Scene.heat_animation_id_downloading
        del bpy.types.Scene.heat_animation_results_list
        del bpy.types.Scene.heat_animation_results_list_index
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