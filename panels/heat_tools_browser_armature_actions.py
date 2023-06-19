import bpy


class HeatToolsBrowserArmatureActionsPanel(bpy.types.Panel):
    bl_idname = "HEAT_TOOLS_BROWSER_PT_armature_actions_panel"
    bl_label = "HeatTools Armature"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HeatTools"
    bl_order = 1


    def draw(self, context):
        layout = self.layout
        layout.label(text="Armature actions:")
        layout.operator("heat.import_t69h_armature", text="Import New Armature")
        layout.operator("heat.import_t69h", text="Import Armature+Mesh")
        layout.operator("heat.bind_t69h_with_auto_weights")
        layout.operator("heat.swap_hips_root_location_fcurves")

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)
