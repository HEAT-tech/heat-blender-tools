import bpy
from .panels import *
from .operators import *
from .custom_types import *

bl_info = {
    "name": "HeatBlender",
    "author": "Alfredo Gonzalez-Martinez",
    "description": "Heat tools for Blender",
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "",
    "category": "Generic"
}

classes = (
    ZeroRootOperator,
    RenameBonesOperator,
    UniformScaleArmatureOperator,
    ZeroArmatureLocationOperator,
    MultiexporterOperator,
    ProcessBatchOperator,
    ImportDirOperator,
    ExportOperator,
    APISearchAnimationsOperator,

    HeatAnimationResultListItem,
    HeatAnimationResultsList,

    HeatToolsBatchPanel,
    HeatToolsPanel,
    HeatToolsBrowserPanel
)

register, unregister = bpy.utils.register_classes_factory(classes)