import bpy
from .panels import *
from .operators import *
from .custom_types import *
from .services import AsyncLoopModalOperator, AsyncModalOperatorMixin, setup_asyncio_executor

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
    APIDownloadAnimationOperator,

    HeatAnimationResultListItem,
    HeatAnimationResultsList,

    HeatToolsBatchPanel,
    HeatToolsPanel,
    HeatToolsBrowserPanel
)

factory_register, factory_unregister = bpy.utils.register_classes_factory(classes)

def register():
    factory_register()

    setup_asyncio_executor()
    bpy.utils.register_class(AsyncLoopModalOperator)

def unregister():
    factory_unregister()
    bpy.utils.unregister_class(AsyncLoopModalOperator)