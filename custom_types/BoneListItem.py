import bpy
from bpy.types import PropertyGroup, UIList
from bpy.props import StringProperty, BoolProperty

class BoneListItem(PropertyGroup):
    """Properties of the bone list items"""
    bone_name_source: StringProperty(
        name="Source Bone",
        description="The source bone name",
        default="")

    bone_name_target: StringProperty(
        name="Target Bone",
        description="The target bone name",
        default="")

    bone_name_key: StringProperty(
        name="Auto Detection Key",
        description="The automatically detected bone key",
        default="")

    is_custom: BoolProperty(
        description="This determines if the field is a custom one source bone one",
        default=False)
