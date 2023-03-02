import bpy
from .. import services

class BPMQuantizeKeyframesOperator(bpy.types.Operator):
    """Open a URL in the default web browser"""
    bl_idname = "heat.bpm_quantize_keyframes"
    bl_label = "Quantize selected keyframes to BPM markers"

    def execute(self, context):
        bpm_service = services.bpm_service.BPMService(context.scene.heat_bpm)
        obj = bpy.context.active_object
        action = obj.animation_data.action

        for fcurve in action.fcurves :
            for p in fcurve.keyframe_points :
                if p.select_control_point:
                    keyframe_frame = p.co[0]
                    nearest_grid_frame = bpm_service.get_nearest_frame_to_grid(keyframe_frame, context.scene.heat_quantize_note)
                    p.co[0] = nearest_grid_frame
            fcurve.update()
        return {'FINISHED'}


    @classmethod
    def register(cls):

        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        print("Unregistered: %s" % cls.bl_label)



