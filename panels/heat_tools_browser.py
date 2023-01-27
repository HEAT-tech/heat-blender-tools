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
        layout.label(text="Browse HEAT Animations")
        layout.separator()

        layout.operator("heat.api_search_animations")

        layout.template_list(
            "HeatAnimationResultsList",
            "Heat_Animation_Results_List",
            context.scene,
            "heat_animation_results_list",
            context.scene,
            "heat_animation_results_list_index"
        )
        # layout.operator("heat.api_preview_animation")

        tpath = get_addon_thumbnail_path('dummy.png')
        img = bpy.data.images.load(tpath, check_existing = True)
        preview = img.preview_ensure()

        layout.separator()
        layout.label(text="Preview:")
        layout.template_icon(icon_value=preview.icon_id, scale=10.0)


    @classmethod
    def register(cls):
        bpy.types.Scene.heat_animation_results_list = bpy.props.CollectionProperty(
            type=custom_types.HeatAnimationResultListItem
        )
        bpy.types.Scene.heat_animation_results_list_index = bpy.props.IntProperty(
            name = "Index for Heat animation results",
            default = 0
        )
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.heat_animation_results_list
        del bpy.types.Scene.heat_animation_results_list_index
        print("Unregistered: %s" % cls.bl_label)