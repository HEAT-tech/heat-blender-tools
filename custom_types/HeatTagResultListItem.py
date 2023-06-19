import bpy


class HeatTagResultListItem(bpy.types.PropertyGroup):
    """Property group representing a tag from the Heat API"""
    id: bpy.props.IntProperty(
        name="ID",
        description="Tag ID",
        default=1
    )

    parent_id: bpy.props.IntProperty(
        name="ID",
        description="Tag Parent ID",
        default=0
    )

    name: bpy.props.StringProperty(
        name="Name",
        description="Tag name",
        default="Heat Tag"
    )

    url: bpy.props.StringProperty(
        name="URL",
        description="Tag url",
        default="https://heat.tag.tech"
    )

    selected: bpy.props.BoolProperty(default=False)

