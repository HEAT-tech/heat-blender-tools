import bpy
from .. import custom_types
import os


def get_addon_thumbnail_path(name):
    script_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(script_path, f"..{os.sep}assets")
    # fpath = os.path.join(p, subpath)
    ext = name.split('.')[-1]
    next = ''
    if not (ext == 'jpg' or ext == 'png'):  # already has ext?
        next = '.jpg'
    subpath = f"img{os.sep}{name}{next}"
    return os.path.join(script_path, subpath)


class HeatToolsBrowserPanel(bpy.types.Panel):
    bl_idname = "HEAT_TOOLS_BROWSER_PT_panel"
    bl_label = "HeatTools Browser"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HeatTools"
    bl_order = 0

    def draw(self, context):
        layout = self.layout

        if not context.scene.heat_auth_is_logged_in:
            self.draw_auth(context, layout)
            return

        layout.label(text="Browse HEAT Animations")
        layout.separator()

        layout.operator("heat.api_search_animations")

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

        self.draw_heat_animation_preview(context, layout)

        layout.operator("heat.download_animation", icon="IMPORT", text="Download")


    def draw_auth(self, context, layout):
        layout.label(text="You are not logged in...")
        layout.operator("heat.auth_login")
        layout.operator("heat.auth_register")

    def draw_heat_animation_preview(self, context, layout):
        layout.label(text="Preview:")
        preview_box = layout.box()
        if context.scene.heat_animation_results_list_index >= 0:
            tpath = get_addon_thumbnail_path('dummy.png')
        else:
            tpath = get_addon_thumbnail_path('heat.png')

        img = bpy.data.images.load(tpath, check_existing = True)
        preview = img.preview_ensure()
        preview_box.template_icon(icon_value=preview.icon_id, scale=10.0)


    @classmethod
    def register(cls):
        bpy.types.Scene.heat_auth_is_logged_in = bpy.props.BoolProperty(
            name = "Heat authentication state",
            default = True
        )

        bpy.types.Scene.heat_animation_results_loading = bpy.props.BoolProperty(
            name = "Heat animation results fetch state",
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
        del bpy.types.Scene.heat_auth_is_logged_in
        del bpy.types.Scene.heat_animation_results_loading
        del bpy.types.Scene.heat_animation_results_list
        del bpy.types.Scene.heat_animation_results_list_index
        print("Unregistered: %s" % cls.bl_label)