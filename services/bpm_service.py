import bpy


class BPMService:
    def __init__(self, bpm, crotchets_per_measure=4, crotchets_denominator=4):
        self.bpm = bpm
        self.fps = bpy.context.scene.render.fps
        self.crotchets_per_measure = crotchets_per_measure
        self.crotchets_denominator = crotchets_denominator

        self.beat_duration = 60 / bpm
        self.crotchet_duration = self.beat_duration * (4 / crotchets_denominator)
        self.measure_duration = self.crotchet_duration * crotchets_denominator

        self.frames_per_measure = self.fps * self.measure_duration
        self.frames_per_crotchet = self.fps * (self.crotchet_duration / (1 / crotchets_per_measure))


    def get_nearest_frame_to_grid(self, frame, nearest_crotchet_value=4):
        """
        Given a frame number, quantize and return the new frame value. Set nearest_crotchet_value to tighten/grow grid
        return the nearest frame number which is quantized
        :param frame: frame to be quantized
        :param nearest_crotchet_value: 2, 4, 8, or 16 for half, quarter, eighth, and 16th note grid
        """
        grid_frames = self.get_grid_frames(nearest_crotchet_value)

        nearest_distance = float("inf")
        nearest_grid_frame = None
        for grid_frame in grid_frames:
            distance = abs(grid_frame - frame)
            if distance < nearest_distance:
                nearest_grid_frame = grid_frame
                nearest_distance = distance

        return nearest_grid_frame


    def get_grid_frames(self, nearest_crotchet_value=4):
        """
        :return: array of frames which lie within the grid
        :param nearest_crotchet_value: 2, 4, 8, or 16 for half, quarter, eighth, and 16th note grid
        """
        scene = bpy.context.scene
        end_frame = scene.frame_end

        grid_frames = []
        for frame in range(1, end_frame + 1):
            if frame == 1:
                grid_frames.append(frame)
                continue

            resolution = nearest_crotchet_value / 4
            frame_in_measure = frame % (self.frames_per_measure / (self.crotchets_denominator * resolution))

            if round(frame_in_measure % self.frames_per_crotchet, 2) <= 0.99 :
                grid_frames.append(frame)

        return grid_frames