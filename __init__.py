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
    AuthGetAPIKeyOperator,
    ImportT69HOperator,
    ImportT69HArmatureOperator,
    BindWithAutoWeightsOperator,
    BPMMarkerGeneratorOperator,

    HeatAnimationResultListItem,
    HeatAnimationResultsList,

    HeatToolsBatchPanel,
    HeatToolsPanel,
    HeatToolsBrowserPanel,
    HeatToolsBPMToolPanel,
)


factory_register, factory_unregister = bpy.utils.register_classes_factory(classes)


class HeatAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    show_heat_advanced_panels: bpy.props.BoolProperty(
        name="Show Advanced Heat Panels",
        description="Show advanced panels",
        default=False
    )

    heat_user_api_key: bpy.props.StringProperty(
        name="Heat API Key",
        subtype='PASSWORD',
        default='d7b8ed1fdb12327c3d2dcb8963297ea6'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "heat_user_api_key")
        layout.operator("heat.auth_get_api_key")
        layout.prop(self, "show_heat_advanced_panels")


def register():
    bpy.utils.register_class(HeatAddonPreferences)
    factory_register()

    setup_asyncio_executor()
    bpy.utils.register_class(AsyncLoopModalOperator)


def unregister():
    bpy.utils.unregister_class(HeatAddonPreferences)
    factory_unregister()
    bpy.utils.unregister_class(AsyncLoopModalOperator)
