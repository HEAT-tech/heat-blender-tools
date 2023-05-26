import bpy

from ..lib.retargeting import get_target_armature, get_source_armature

from bpy.types import PropertyGroup, UIList
from bpy.props import StringProperty, BoolProperty


# Retargeting panel
class HeatToolsRetargetingPanel(bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_heat_retargeting'
    bl_label = 'Heat Retargeting'
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HeatTools"
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = False

        row = layout.row(align=True)
        row.label(text='Select the armatures:')

        row = layout.row(align=True)
        row.prop(context.scene, 'heat_retargeting_armature_source', icon='ARMATURE_DATA')

        row = layout.row(align=True)
        row.prop(context.scene, 'heat_retargeting_armature_target', icon='ARMATURE_DATA')

        anim_exists = False
        for obj in bpy.data.objects:
            if obj.animation_data and obj.animation_data.action:
                anim_exists = True

        if not anim_exists:
            row = layout.row(align=True)
            row.label(text='No animated armature found!', icon='INFO')
            return

        if not context.scene.heat_retargeting_armature_source or not context.scene.heat_retargeting_armature_target:
            self.draw_import_export(layout)
            return

        if not context.scene.heat_retargeting_bone_list:
            row = layout.row(align=True)
            row.scale_y = 1.2
            row.operator('heat.build_bone_list')
            self.draw_import_export(layout)
            return

        subrow = layout.row(align=True)
        row = subrow.row(align=True)
        row.scale_y = 1.2
        row.operator('heat.build_bone_list', text='Rebuild Bone List')
        row = subrow.row(align=True)
        row.scale_y = 1.2
        row.alignment = 'RIGHT'
        row.operator('heat.clear_bone_list', text="", icon='X')

        layout.separator()

        row = layout.row(align=True)
        row.template_list("HEAT_UL_BoneList", "Bone List", context.scene, "heat_retargeting_bone_list", context.scene, "heat_retargeting_bone_list_index", rows=1, maxrows=10)

        row = layout.row(align=True)
        row.operator('heat.add_bone_list_item', text="Add Custom Entry", icon='ADD')

        row = layout.row(align=True)
        row.prop(context.scene, 'heat_retargeting_auto_scaling')

        row = layout.row(align=True)
        row.label(text='Use Pose:')
        row.prop(context.scene, 'heat_retargeting_use_pose', expand=True)

        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator('heat.retarget_animation')

        self.draw_import_export(layout)

    def draw_import_export(self, layout):
        layout.separator()

        row = layout.row(align=True)
        row.label(text='Custom Naming Schemes:')

        subrow = layout.row(align=True)
        row = subrow.row(align=True)
        row.scale_y = 0.9
        row.operator('heat.save_custom_bones_retargeting', text='Save')
        row.operator('heat.import_custom_schemes', text='Import')
        row.operator('heat.export_custom_schemes', text='Export')
        row = subrow.row(align=True)
        row.scale_y = 0.9
        row.alignment = 'RIGHT'
        row.operator('heat.clear_custom_bones', text='', icon='X')


class BoneListItem(PropertyGroup):
    """Properties of the bone list items"""
    bone_name_source: StringProperty(
        name="Source Bone",
        description="The source bone name",
        default="")

    bone_name_target: StringProperty(
        name="Target Bone",
        description="The target bone name",
        default="")

    bone_name_key: StringProperty(
        name="Auto Detection Key",
        description="The automatically detected bone key",
        default="")

    is_custom: BoolProperty(
        description="This determines if the field is a custom one source bone one",
        default=False)



class HEAT_UL_BoneList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        armature_target = get_target_armature()
        armature_source = get_source_armature()

        layout = layout.split(factor=0.36, align=True)

        # Displays source bone
        if item.is_custom:
            layout.prop_search(item, 'bone_name_source', armature_source.pose, "bones", text='')
        else:
            layout.label(text=item.bone_name_source)

        # Displays target bone
        if armature_target:
            layout.prop_search(item, 'bone_name_target', armature_target.pose, "bones", text='')
