import bpy

class PoseToRest(bpy.types.Operator):
    bl_idname = 'heat.pose_to_rest'
    bl_label = 'Pose to Rest'
    bl_description = 'Thoroughly apply current pose as rest pose.\nUseful for applying T-pose on an A-pose armature.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = get_armature()
        return armature and armature.mode == 'POSE'

    def execute(self, context):
        # Retrieve the armature we're operating on
        armature = get_armature()

        # If we can't find the armature, abort
        if not armature:
            self.report({'ERROR'}, 'No suitable armature found.')
            return {'CANCELLED'}

        # Ensure we're in object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # For each mesh associated with the specific armature
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for mod in obj.modifiers:
                    # Check if the mesh has an armature modifier pointing to our specific armature
                    if mod.type == 'ARMATURE' and mod.object == armature:
                        # Duplicate the modifier
                        duplicate_mod = obj.modifiers.new(name=mod.name + "_duplicate", type='ARMATURE')
                        duplicate_mod.object = armature
                        duplicate_mod.use_vertex_groups = mod.use_vertex_groups

                        # Apply the original modifier
                        bpy.context.view_layer.objects.active = obj
                        bpy.ops.object.modifier_apply(modifier=mod.name)

        # Now, go into pose mode and apply pose as rest pose
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.armature_apply()

        self.report({'INFO'}, 'Pose to Rest completed.')
        return {'FINISHED'}


def get_armature(armature_name=None):
    # If a specific name is provided, use it
    if armature_name:
        return bpy.data.objects.get(armature_name)

    # If we're in POSE mode, return the active armature
    if bpy.context.active_object and bpy.context.active_object.type == 'ARMATURE' and bpy.context.mode == 'POSE':
        return bpy.context.active_object

    # If the scene has an armature attribute, return it
    if hasattr(bpy.context.scene, 'armature'):
        return bpy.data.objects.get(bpy.context.scene.armature)

    return None

