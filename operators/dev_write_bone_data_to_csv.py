import bpy
import csv



class DevWriteBoneDataToCSVOperator(bpy.types.Operator):
    """Write Bone Data to CSV"""
    bl_idname = "heat.dev_write_bone_data_to_csv"
    bl_label = "Write Bone Data to CSV"

    directory: bpy.props.StringProperty(name="Directory")
    filename: bpy.props.StringProperty(name="File Name")
    filepath: bpy.props.StringProperty(name="File Path")

    def execute(self, context):
        csv_file_path = self.filepath

        selected_pose_bones = bpy.context.selected_pose_bones
        frame_range = range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1)

        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)

            # Write the CSV headers
            headers = ['Frame']
            for bone in selected_pose_bones:
                headers += [f"{bone.name}.X", f"{bone.name}.Y", f"{bone.name}.Z"]
            writer.writerow(headers)

            # Write the location data for each frame
            for frame in frame_range:
                row_data = [frame]
                bpy.context.scene.frame_set(frame)
                for bone in selected_pose_bones:
                    location = bone.location
                    row_data += [location.x, location.y, location.z]
                writer.writerow(row_data)
        return {'FINISHED'}

    def invoke(self, context, event):
        # Open browser, take reference to 'self' read the path to selected
        # file, put path in predetermined self fields.
        # See: https://docs.blender.org/api/current/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
        context.window_manager.fileselect_add(self)
        # Tells Blender to hang on for the slow user input
        return {'RUNNING_MODAL'}
