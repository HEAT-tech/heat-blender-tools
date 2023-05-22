import bpy


class HeatToolsNLAToolPanel(bpy.types.Panel):
    bl_idname = "heat_tools_nla_tool_pt_panel"
    bl_label = "HeatTools NLA Tool"
    bl_space_type = 'NLA_EDITOR'
    bl_region_type = 'UI'
    bl_category = "HeatTools NLA"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        selected_strips = get_selected_nla_strips()
        return len(selected_strips) == 2


    def draw(self, context):
        layout = self.layout

        layout.label(text="Bone Sync:")
        layout.prop(context.scene, 'heat_action_hip_sync_axis_vector', text="Sync")
        layout.operator("heat.action_hip_sync", icon="ARMATURE_DATA")
        layout.separator()

        layout.label(text="Action Strip Bake:")
        layout.operator("heat.bake_actions")


    @classmethod
    def register(cls):
        bpy.types.Scene.heat_action_hip_sync_axis_vector = bpy.props.BoolVectorProperty(
            name="Action sync axis",
            subtype='XYZ',
            default=(True, True, True),
            description="Vector property for heat action sync"
        )
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.heat_action_hip_sync_axis_vector
        print("Unregistered: %s" % cls.bl_label)


def get_selected_nla_strips():
    selected_strips = []
    for obj in bpy.data.objects:
        if obj.animation_data and obj.animation_data.nla_tracks:
            for track in obj.animation_data.nla_tracks:
                for strip in track.strips:
                    if strip.select:
                        selected_strips.append(strip)
    return selected_strips