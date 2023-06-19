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

    preview_image_url: bpy.props.StringProperty(
        name="Preview Image Url",
        description="Animation preview image Url",
        default=""
    )


    url: bpy.props.StringProperty(
        name="Animation Url",
        description="Animation Url",
        default=""
    )

    tags: bpy.props.CollectionProperty(
        name="Animation Tags",
        type=bpy.types.PropertyGroup
    )


class HeatAnimationResultListTagItem(bpy.types.PropertyGroup):
    """Property group representing a tag associated with an animation from the Heat API"""
    id: bpy.props.IntProperty(
        name="Tag ID",
        description="Tag ID",
        default=0
    )
    url: bpy.props.StringProperty(
        name="Tag URL",
        description="Tag URL",
        default=""
    )
    parent_id: bpy.props.IntProperty(
        name="Tag parent ID",
        description="Tag parent ID",
        default=-1
    )
    name: bpy.props.StringProperty(
        name="Tag name",
        description="Tag name",
        default="Animation Tag"
    )