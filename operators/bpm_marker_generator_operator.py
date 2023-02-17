import bpy
import webbrowser

class BPMMarkerGeneratorOperator(bpy.types.Operator):
    """Open a URL in the default web browser"""
    bl_idname = "heat.bpm_marker_generator"
    bl_label = "Generate markers on bpm downbeat"

    def execute(self, context):
        bpm = context.scene.heat_bpm
        crotchets_per_measure = context.scene.heat_bpm_crotchets_per_measure
        crotchets_denominator = context.scene.heat_bpm_crotchets_denominator
        self.generate_downbeats(bpm, crotchets_per_measure, crotchets_denominator)
        return {'FINISHED'}

    def generate_downbeats(self, bpm, crotchets_per_measure=4, crotchets_denominator=4):
        scene = bpy.context.scene
        fps = scene.render.fps
        end_frame = scene.frame_end

        # clear current timeline markers
        scene.timeline_markers.clear()

        beat_duration = 60 / bpm
        crotchet_duration = beat_duration * (4 / crotchets_denominator)
        measure_duration = crotchet_duration * crotchets_denominator

        # Calculate the number of frames per measure and crotchet
        frames_per_measure = fps * measure_duration
        frames_per_crotchet = fps * (crotchet_duration / (1 / crotchets_per_measure))

        beat = 1
        bar = 1
        for frame in range(1, end_frame + 1):
            if frame == 1:
                self.set_marker(frame, bar, beat)
                continue

            frame_in_measure = frame % (frames_per_measure / crotchets_denominator)

            if round(frame_in_measure % frames_per_crotchet, 2) <= 0.99 :
                beat += 1
                if beat % (crotchets_per_measure+1) == 0:
                    beat = 1
                    bar += 1
                self.set_marker(frame, bar, beat)


    def set_marker(self, frame, bar, beat):
        marker_text = f'{bar}.{beat}'
        bpy.context.scene.timeline_markers.new(marker_text, frame=frame)


    @classmethod
    def register(cls):
        bpy.types.Scene.heat_bpm = bpy.props.IntProperty(
            name = "Heat BPM",
            default = 128
        )
        bpy.types.Scene.heat_bpm_crotchets_per_measure = bpy.props.IntProperty(
            name = "Heat BPM crotchets",
            default = 4
        )
        bpy.types.Scene.heat_bpm_crotchets_denominator = bpy.props.IntProperty(
            name = "Heat BPM crotchets per measure",
            default = 4,
            step = 2
        )
        print("Registered: %s" % cls.bl_label)

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.heat_bpm
        del bpy.types.Scene.heat_bpm_crotchets_per_measure
        del bpy.types.Scene.heat_bpm_crotchets_denominator
        print("Unregistered: %s" % cls.bl_label)