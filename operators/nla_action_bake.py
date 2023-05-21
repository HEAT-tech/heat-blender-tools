import bpy
from bpy.props import IntProperty, BoolProperty, EnumProperty
from bpy_types import Operator


class BakeSelectedActionsOperator(Operator):
    """Bake all selected objects location/scale/rotation animation to an action"""
    bl_idname = "heat.bake_actions"
    bl_label = "Quick Bake Action (Heat)"
    bl_options = {'REGISTER', 'UNDO'}

    frame_start: IntProperty(
        name="Start Frame",
        description="Start frame for baking",
        min=0, max=300000,
        default=1,
    )
    frame_end: IntProperty(
        name="End Frame",
        description="End frame for baking",
        min=1, max=300000,
        default=250,
    )
    step: IntProperty(
        name="Frame Step",
        description="Frame Step",
        min=1, max=120,
        default=1,
    )
    only_selected: BoolProperty(
        name="Only Selected Bones",
        description="Only key selected bones (Pose baking only)",
        default=False,
    )
    visual_keying: BoolProperty(
        name="Visual Keying",
        description="Keyframe from the final transformations (with constraints applied)",
        default=True,
    )
    clear_constraints: BoolProperty(
        name="Clear Constraints",
        description="Remove all constraints from keyed object/bones, and do 'visual' keying",
        default=False,
    )
    clear_parents: BoolProperty(
        name="Clear Parents",
        description="Bake animation onto the object then clear parents (objects only)",
        default=False,
    )
    use_current_action: BoolProperty(
        name="Overwrite Current Action",
        description="Bake animation into current action, instead of creating a new one "
        "(useful for baking only part of bones in an armature)",
        default=False,
    )
    clean_curves: BoolProperty(
        name="Clean Curves",
        description="After baking curves, remove redundant keys",
        default=False,
    )
    bake_types: EnumProperty(
        name="Bake Data",
        description="Which data's transformations to bake",
        options={'ENUM_FLAG'},
        items=(
             ('POSE', "Pose", "Bake bones transformations"),
             ('OBJECT', "Object", "Bake object transformations"),
        ),
        default={'POSE'},
    )

    @classmethod
    def poll(cls, context):
        selected_strips = get_selected_nla_strips()
        return len(selected_strips) >= 2

    def execute(self, context):
        from bpy_extras import anim_utils
        do_pose = 'POSE' in self.bake_types
        do_object = 'OBJECT' in self.bake_types

        if do_pose and self.only_selected:
            pose_bones = context.selected_pose_bones or []
            armatures = {pose_bone.id_data for pose_bone in pose_bones}
            objects = list(armatures)
        else:
            objects = context.selected_editable_objects
            if do_pose and not do_object:
                objects = [obj for obj in objects if obj.pose is not None]

        object_action_pairs = (
            [(obj, getattr(obj.animation_data, "action", None)) for obj in objects]
            if self.use_current_action else
            [(obj, None) for obj in objects]
        )

        selected_strips = get_selected_nla_strips()
        min_start_frame, max_end_frame = get_selected_nla_strips_range(selected_strips)
        self.frame_start = int(min_start_frame)
        self.frame_end = int(max_end_frame)

        actions = anim_utils.bake_action_objects(
            object_action_pairs,
            frames=range(self.frame_start, self.frame_end + 1, self.step),
            only_selected=self.only_selected,
            do_pose=do_pose,
            do_object=do_object,
            do_visual_keying=self.visual_keying,
            do_constraint_clear=self.clear_constraints,
            do_parents_clear=self.clear_parents,
            do_clean=self.clean_curves,
        )

        if not any(actions):
            self.report({'INFO'}, "Nothing to bake, make sure object and actions selected.")
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, _event):
        scene = context.scene
        if scene.use_preview_range:
            self.frame_start = scene.frame_preview_start
            self.frame_end = scene.frame_preview_end
        else:
            selected_strips = get_selected_nla_strips()
            min_start_frame, max_end_frame = get_selected_nla_strips_range(selected_strips)
            self.frame_start = int(min_start_frame)
            self.frame_end = int(max_end_frame)
        self.bake_types = {'POSE'} if context.mode == 'POSE' else {'OBJECT'}

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def menu_func(self, context):
        self.layout.operator(BakeSelectedActionsOperator.bl_idname, icon="ARMATURE_DATA")

    @classmethod
    def register(cls):
        bpy.types.NLA_MT_context_menu.append(cls.menu_func)
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        bpy.types.NLA_MT_context_menu.remove(cls.menu_func)
        print("Unregistered: %s" % cls.bl_label)

def get_selected_nla_strips():
    selected_strips = []
    for obj in bpy.data.objects:
        if obj.animation_data and obj.animation_data.nla_tracks:
            for track in obj.animation_data.nla_tracks:
                for strip in track.strips:
                    if strip.select:
                        selected_strips.append(strip)
    return selected_strips

def get_selected_nla_strips_range(selected_strips):
    if not selected_strips:
        return None

    # Initialize with the start and end frames of the first strip.
    min_start_frame = selected_strips[0].frame_start
    max_end_frame = selected_strips[0].frame_end

    for strip in selected_strips[1:]:  # Skip the first strip since we've already processed it.
        min_start_frame = min(min_start_frame, strip.frame_start)
        max_end_frame = max(max_end_frame, strip.frame_end)

    return min_start_frame, max_end_frame
