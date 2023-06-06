import bpy


class ActionHipSyncOperator(bpy.types.Operator):
    """Download Heat Animation"""
    bl_idname = "heat.action_hip_sync"
    bl_label = "Sync Bone Positions"
    bl_description = "Sync the bone position of two actions"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        selected_strips = get_selected_nla_strips()
        return len(selected_strips) == 2

    def execute(self, context):
        selected_strips = get_selected_nla_strips()
        print(f"Num strips selected: {len(selected_strips)}")
        for strip in selected_strips:
            print(f"Object: {strip.id_data.name}, Strip: {strip.name}, Action: {strip.action.name}")


        if len(selected_strips) >= 2:
            last_start_strip, first_strip = self.strip_starting_last(selected_strips[0], selected_strips[1])
            last_start_frame = last_start_strip.frame_start
            first_start_frame = first_strip.frame_start

            print(f"First strip: {first_strip.name} (starts at: {first_start_frame}")
            print(f"Last strip: {last_start_strip.name} (starts at: {last_start_frame}")

            bone_name = context.scene.heat_action_hip_sync_bone
            location_path = f'pose.bones["{bone_name}"].location'
            # rotation_path = f'pose.bones["{bone_name}"].rotation_quaternion'

            last_start_action = last_start_strip.action
            first_action = first_strip.action

            loc_diff = [0, 0, 0]
            # rot_diff = [0, 0, 0, 0]

            for i in range(3):
                start_frame = last_start_frame - first_start_frame
                first_loc = first_action.fcurves.find(location_path, index=i).evaluate(start_frame)
                last_start_loc = last_start_action.fcurves.find(location_path, index=i).evaluate(0)
                loc_diff[i] = first_loc - last_start_loc


            # swap y and z axis as the bones have those axis flipped
            enabled_axis = [True, True, True]
            sync_axis_vector = context.scene.heat_action_hip_sync_axis_vector
            enabled_axis[0] = sync_axis_vector[0]
            enabled_axis[1] = sync_axis_vector[2]
            enabled_axis[2] = sync_axis_vector[1]

            # replace keyframes
            for i in range(3):
                if enabled_axis[i] == False:
                    continue

                loc_fcurve = last_start_action.fcurves.find(location_path, index=i)
                loc_kp_i = 0
                for kp in loc_fcurve.keyframe_points:
                    kp = loc_fcurve.keyframe_points[loc_kp_i]
                    loc_kp_i += 1
                    frame = kp.co[0]
                    original_value = kp.co[1]
                    corrected_value = original_value + loc_diff[i]

                    # print(f"updating location...{i}: {kp.co[0]}")

                    # remove keyframe points already at frame
                    loc_fcurve.keyframe_points.remove(kp)

                    # insert corrected keyframe points
                    loc_fcurve.keyframe_points.insert(frame, corrected_value)
                    loc_fcurve.keyframe_points.update()

            print(f"done.... {last_start_strip.name} ")
        return {'FINISHED'}


    def get_selected_nla_strips(self):
        selected_strips = []
        for obj in bpy.data.objects:
            if obj.animation_data and obj.animation_data.nla_tracks:
                for track in obj.animation_data.nla_tracks:
                    for strip in track.strips:
                        if strip.select:
                            selected_strips.append(strip)
        return selected_strips

    def strip_starting_last(self, strip1, strip2):
        if strip1.frame_start > strip2.frame_start:
            return strip1, strip2
        else:
            return strip2, strip1

    def menu_func(self, context):
        self.layout.operator(ActionHipSyncOperator.bl_idname, icon="ARMATURE_DATA")

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