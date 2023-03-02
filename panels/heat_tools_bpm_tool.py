import bpy
from .. import custom_types


class HeatToolsBPMToolPanel(bpy.types.Panel):
    bl_idname = "HEAT_TOOLS_BPM_Tool_PT_panel"
    bl_label = "HeatTools BPM Tool"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HeatTools BPM"
    bl_order = 0

    def draw(self, context):
        layout = self.layout

        layout.label(text="BPM Tool", icon='TIME')

        layout.prop(context.scene, "heat_bpm", text='BPM')
        layout.separator()

        layout.label(text="Time Signature", icon='MOD_TIME')
        time_signature_row = layout.row()
        time_signature_row.prop(context.scene, "heat_bpm_crotchets_per_measure", text='')
        time_signature_row.label(icon='IPO_LINEAR')
        time_signature_row.prop(context.scene, "heat_bpm_crotchets_denominator", text='')
        layout.separator()
        layout.operator("heat.bpm_marker_generator", text='Generate')


    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)