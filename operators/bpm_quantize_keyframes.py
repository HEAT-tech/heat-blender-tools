import bpy
import webbrowser

class BPMQuantizeKeyframesOperator(bpy.types.Operator):
    """Open a URL in the default web browser"""
    bl_idname = "heat.bpm_quantize_keyframes"
    bl_label = "Quantize selected keyframes to BPM markers"

    def execute(self, context):
        self.snap_keyframe_to_nearest_time_marker()
        return {'FINISHED'}

    def snap_keyframe_to_nearest_time_marker(self):
        # Get the current frame and all markers in the timeline
        current_frame = bpy.context.scene.frame_current
        markers = bpy.context.scene.timeline_markers

        # Find the nearest marker to the current frame
        nearest_marker = None
        nearest_distance = float("inf")
        for marker in markers:
            distance = abs(current_frame - marker.frame)
            if distance < nearest_distance:
                nearest_marker = marker
                nearest_distance = distance

        if nearest_marker is None:
            return

        # If a nearest marker was found, move the selected keyframe to the marker's frame
        selected_keyframes = bpy.context.selected_keyframes
        for fcurve, keyframe_index in selected_keyframes:
            keyframe = fcurve.keyframe_points[keyframe_index]
            keyframe.co.x = nearest_marker.frame

    @classmethod
    def register(cls):
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)



