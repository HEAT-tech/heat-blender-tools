import bpy


class HeatAnimationResultsList(bpy.types.UIList):
    """Property group representing list of animations from the Heat API"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):

        # We could write some code to decide which icon to use here...
        custom_icon = 'ARMATURE_DATA'
        layout.label(text=item.name, icon=custom_icon)
