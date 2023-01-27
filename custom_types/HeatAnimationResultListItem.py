import bpy


class HeatAnimationResultListItem(bpy.types.PropertyGroup):
    """Property group representing an animation from the Heat API"""

    name: bpy.props.StringProperty(
        name="Name",
        description="Animation name",
        default="Heat Animation"
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
