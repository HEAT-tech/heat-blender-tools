import bpy
import os
import pkg_resources
import functools
from . import dependencies
from . import addon_updater_ops
from .simple_queue import SimpleQueue
from .dotenv import DotENV


bl_info = {
    "name": "HeatBlender",
    "author": "Alfredo Gonzalez-Martinez",
    "description": "Heat tools for Blender",
    "version": (1, 1, 0),
    "blender": (3, 20, 0),
    "location": "View3D",
    "warning": "",
    "category": "3D View"
}


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
    from . import local_server
    from .local_server_health_checker import start_server_if_not_started
    from .queue_worker import work_queue
except:
    ensure_pip_and_install_dependencies()
    from .panels import *
    from .operators import *
    from .custom_types import *
    from .services import AsyncLoopModalOperator, setup_asyncio_executor
    from . import local_server
    from .local_server_health_checker import start_server_if_not_started
    from .queue_worker import work_queue

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
    APIFetchMoreAnimationsOperator,
    APIDownloadAnimationOperator,
    APIFetchTagsOperator,
    AuthGetAPIKeyOperator,
    ImportT69HOperator,
    ImportT69HArmatureOperator,
    BindWithAutoWeightsOperator,
    BPMMarkerGeneratorOperator,
    BPMQuantizeKeyframesOperator,
    DevWriteBoneDataToCSVOperator,
    SwapHipsRootLocationFCurvesOperator,
    ActionHipSyncOperator,
    BakeSelectedActionsOperator,
    IMPORT_SCENE_OT_vrm_as_gltf,
    PoseToRest,
    OpenWebUIOperator,

    # Retargetter
    BuildBoneList,
    HEAT_UL_BoneList,
    AddBoneListItem,
    ClearBoneList,
    RetargetAnimation,
    # Retargetter Detector
    DetectFaceShapes,
    DetectActorBones,
    SaveCustomShapes,
    SaveCustomBones,
    SaveCustomBonesRetargeting,
    ImportCustomBones,
    ExportCustomBones,
    ClearCustomBones,
    ClearCustomShapes,

    HeatAnimationResultListTagItem,
    HeatAnimationResultListItem,
    HeatAnimationResultsList,
    BoneListItem,
    HeatTagResultListItem,
    HeatTagResultsList,

    HeatToolsWebUIPanel,
    HeatToolsBatchPanel,
    HeatToolsPanel,
    HeatToolsBrowserPanel,
    HeatToolsBrowserArmatureActionsPanel,
    HeatToolsRetargetingPanel,
    HeatToolsBPMToolPanel,
    HeatToolsBPMQuantizerPanel,
    HEAT_PT_dev_inspector_panel,
    HeatToolsNLAToolPanel
)


factory_register, factory_unregister = bpy.utils.register_classes_factory(classes)


class HeatAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    show_heat_advanced_panels: bpy.props.BoolProperty(
        name="Show Advanced Heat Panels",
        description="Show advanced panels",
        default=False
    )

    start_daemon_on_startup: bpy.props.BoolProperty(
        name="Start Daemon on Startup",
        description="If enabled, Heat Tools can be controlled by web UI (requires restart)",
        default=True
    )

    heat_user_api_key: bpy.props.StringProperty(
        name="Heat API Key",
        subtype='PASSWORD',
        default=''
    )


    auto_check_update: bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=True)

    updater_interval_months: bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)

    updater_interval_days: bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31)

    updater_interval_hours: bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)

    updater_interval_minutes: bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "heat_user_api_key")
        layout.operator("heat.auth_get_api_key")
        layout.operator("heat.panic_reset")
        layout.prop(self, "show_heat_advanced_panels")
        layout.prop(self, "start_daemon_on_startup")

        addon_updater_ops.update_settings_ui(self, context)


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
    addon_updater_ops.register(bl_info)
    bpy.utils.register_class(HeatAddonPreferences)


    factory_register()
    # register retargetter properties once all dependencies are satisfied
    from .lib import retargetting_properties
    retargetting_properties.register()

    setup_asyncio_executor()
    bpy.utils.register_class(AsyncLoopModalOperator)

    # Start Daemon
    this_plugin_name = __name__.split(".")[0]
    start_daemon_on_startup = bpy.context.preferences.addons[this_plugin_name].preferences.start_daemon_on_startup
    if start_daemon_on_startup:
        heat_queue = SimpleQueue('heat_queue.db')
        heat_queue.create()
        local_server.start()
        bpy.app.timers.register(work_queue, first_interval=5.0, persistent=True)
        bpy.app.timers.register(start_server_if_not_started, first_interval=7.0)

    # read .env file and set specified presets
    env = DotENV()
    env_heat_api_key = env.get('HEAT_API_KEY')
    if env_heat_api_key:
        bpy.context.preferences.addons[this_plugin_name].preferences.heat_user_api_key = env_heat_api_key


def unregister():
    bpy.utils.unregister_class(HeatPanicResetOperator)
    addon_updater_ops.unregister()
    factory_unregister()
    bpy.utils.unregister_class(AsyncLoopModalOperator)

    # Kill Daemon
    this_plugin_name = __name__.split(".")[0]
    start_daemon_on_startup = bpy.context.preferences.addons[this_plugin_name].preferences.start_daemon_on_startup
    if start_daemon_on_startup:
        try:
            # local_server.stop()
            local_server.force_kill()
            bpy.app.timers.unregister(work_queue)
            bpy.app.timers.unregister(start_server_if_not_started)
            heat_queue = SimpleQueue('heat_queue.db')
            heat_queue.destroy()
        except:
            pass

    bpy.utils.unregister_class(HeatAddonPreferences)


if __name__ == "__main__":
    register()