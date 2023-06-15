import bpy


class HeatTagResultsList(bpy.types.UIList):
    """Property group representing list of tags from the Heat API"""
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        # We could write some code to decide which icon to use here...
        layout.label(text=item.name)
