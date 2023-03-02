import bpy


class HeatToolsBPMQuantizerPanel(bpy.types.Panel):
    bl_idname = "HEAT_TOOLS_BPM_Quantizer_PT_panel"
    bl_label = "HeatTools BPM Quantizer"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HeatTools BPM"
    bl_order = 1

    def draw(self, context):
        layout = self.layout

        layout.label(text="Quantize to nearest:")
        row = layout.row()
        row.prop(context.scene, "heat_quantize_note", text='1        /', )
        row.label(text='note')
        layout.operator("heat.bpm_quantize_keyframes", text='Quantize')


    @classmethod
    def register(cls):
        bpy.types.Scene.heat_quantize_note = bpy.props.IntProperty(default=4, step=2)
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.heat_quantize_note
        print("Unregistered: %s" % cls.bl_label)