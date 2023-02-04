import bpy


class HeatAnimationResultListItem(bpy.types.PropertyGroup):
    """Property group representing an animation from the Heat API"""

    name: bpy.props.StringProperty(
        name="Name",
        description="Animation name",
        default="Heat Animation"
    )

    movement_id: bpy.props.StringProperty(
        name="ID",
        description="Animation ID",
        default="Heat-ID"
    )

    description: bpy.props.StringProperty(
        name="Description",
        description="Animation description",
        default=""
    )

    download_url: bpy.props.StringProperty(
        name="Download Url",
        description="Animation download Url",
        default=""
    )

    url: bpy.props.StringProperty(
        name="Animation Url",
        description="Animation Url",
        default=""
    )
