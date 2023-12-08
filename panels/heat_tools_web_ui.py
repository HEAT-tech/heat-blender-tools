import bpy


class HeatToolsWebUIPanel(bpy.types.Panel):
    bl_idname = "HEAT_TOOLS_WEB_UI_PT_panel"
    bl_label = "HeatTools WebUI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "HeatTools"
    bl_order = 0
    # bl_options = {'DEFAULT_OPEN'}

    @classmethod
    def poll(self, context):
        this_plugin_name = __name__.split(".")[0]
        start_daemon_on_startup = context.preferences.addons[this_plugin_name].preferences.start_daemon_on_startup
        return start_daemon_on_startup

    def draw(self, context):
        layout = self.layout
        # layout.label(text="Daemon running", icon='COLORSET_02_VEC')
        layout.operator("heat.open_web_ui")

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)