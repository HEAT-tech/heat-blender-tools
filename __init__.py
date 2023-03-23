import bpy
import pkg_resources
from . import dependencies


def ensure_pip_and_install_dependencies():
    import ensurepip
    ensurepip.bootstrap()
    os.environ.pop("PIP_REQ_TRACKER", None)

    # Create a copy of the environment variables and modify them for the subprocess call
    environ_copy = dict(os.environ)
    environ_copy["PYTHONNOUSERSITE"] = "1"

    dependencies.ensure_preinstalled_deps_copied()
    dependencies.add_installed_deps_path()
    dependencies.add_preinstalled_deps_path()
    dependencies.ensure_deps()


try:
    from .panels import *
    from .operators import *
    from .custom_types import *
    from .services import AsyncLoopModalOperator, setup_asyncio_executor
except:
    ensure_pip_and_install_dependencies()
    from .panels import *
    from .operators import *
    from .custom_types import *
    from .services import AsyncLoopModalOperator, setup_asyncio_executor


bl_info = {
    "name": "HeatBlender",
    "author": "Alfredo Gonzalez-Martinez",
    "description": "Heat tools for Blender",
    "blender": (2, 80, 0),
    "location": "View3D",
    "warning": "",
    "category": "3D View"
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
    BPMQuantizeKeyframesOperator,
    DevWriteBoneDataToCSVOperator,

    HeatAnimationResultListItem,
    HeatAnimationResultsList,

    HeatToolsBatchPanel,
    HeatToolsPanel,
    HeatToolsBrowserPanel,
    HeatToolsBPMToolPanel,
    HeatToolsBPMQuantizerPanel,
    HEAT_PT_dev_inspector_panel
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
        default=''
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "heat_user_api_key")
        layout.operator("heat.auth_get_api_key")
        layout.operator("heat.panic_reset")
        layout.prop(self, "show_heat_advanced_panels")


def register():
    # check if required packages are installed.
    this_dir = os.path.dirname(os.path.realpath(__file__))
    requirements = os.path.join(this_dir, 'requirements.txt')
    try:
        pkg_resources.require(open(requirements,mode='r'))
    except:
        # install pip requirements from requirements.txt
        ensure_pip_and_install_dependencies()

    bpy.utils.register_class(HeatPanicResetOperator)
    bpy.utils.register_class(HeatAddonPreferences)
    factory_register()

    setup_asyncio_executor()
    bpy.utils.register_class(AsyncLoopModalOperator)


def unregister():
    bpy.utils.unregister_class(HeatPanicResetOperator)
    bpy.utils.unregister_class(HeatAddonPreferences)
    factory_unregister()
    bpy.utils.unregister_class(AsyncLoopModalOperator)


if __name__ == "__main__":
    register()