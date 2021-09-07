import numpy as np
from PIL import Image
        
from osr2mp4.ImageProcess import imageproc
from osr2mp4.Utils.VideoBuffer import VideoBuffer

class Video:
    def __init__(self, settings: object, path: str, video_time: list, resolution: list):
        self.settings: object = settings
        if not settings.settings['Show background video']:
            return
        
        self.path: str = path
        self.start_time: int = video_time[0]
        self.end_time: int = video_time[1]
        self.last_time: int = self.start_time
        self.resolution = resolution
        self.video: VideoBuffer = VideoBuffer.from_file(path, resolution)
        self.delta: int = 1000 / self.video.fps

        self.video.start(self.start_time)

    def add_to_frame(self, bg: Image.Image, np: np.array, time: int):
        if not self.settings.settings['Show background video']:
            return

        while self.last_time < time:
            self.last_time += self.delta
            self.video.update()
        
        # np.fill(0)
        bg.paste(self.video.img_ptr, (
            int((self.resolution[0] - self.video.end_resolution[0]) / 2),
            int((self.resolution[1] - self.video.end_resolution[1]) / 2)        
        ))