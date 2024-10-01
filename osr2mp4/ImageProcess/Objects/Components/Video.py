import os
import shutil
import subprocess
import numpy as np
from PIL import Image

from osr2mp4.Exceptions import FFmpegNotFound
from osr2mp4.ImageProcess import imageproc
from osr2mp4.Utils.VideoBuffer import VideoBuffer


class Video:
    def __init__(self, settings: object, path: str, video_time: list, resolution: list):
        self.settings: object = settings
        if not settings.settings["Show background video"] or not path:
            return
        # ... epic trolling
        self.check_for_ffmpeg()

        self.path: str = path
        self.start_time: int = video_time[0]
        self.end_time: int = video_time[1]
        self.last_time: int = self.start_time
        self.resolution = resolution
        self.video: VideoBuffer = VideoBuffer.from_file(
            os.path.join(self.settings.beatmap, path), resolution, self.ffmpeg_path
        )
        self.delta: int = 1000 / self.video.fps
        self.ffmpeg_path: str = None
        self.alpha: int = settings.settings["Background dim"]

        self.video.start(self.start_time)

    def check_for_ffmpeg(self) -> None:
        # TODO: shitty check to see if ffmpeg is in PATH env
        ffmpeg_path = shutil.which("ffmpeg")
        ffmpeg_target = ["ffmpeg", "ffmpeg.exe"][os.name == "nt"]

        if not ffmpeg_path:
            if not os.path.exists(ffmpeg_target):
                raise FFmpegNotFound

            ffmpeg_path = ffmpeg_target

        self.ffmpeg_path = ffmpeg_path

    # TODO: fadeout fadein on inbreak and intro
    def add_to_frame(
        self, bg: Image.Image, np: np.array, time: int, in_break: bool
    ) -> None:
        if (
            not self.settings.settings["Show background video"]
            or self.settings.settings["Background dim"] == 100
            or not self.path
        ):
            return

        while self.last_time < time:
            self.last_time += self.delta
            self.video.update()

            imageproc.changealpha(
                self.video.img_ptr, [255 - self.alpha, 255][in_break] / 255
            )

        bg.paste(
            self.video.img_ptr,
            (
                int((self.resolution[0] - self.video.end_resolution[0]) / 2),
                int((self.resolution[1] - self.video.end_resolution[1]) / 2),
            ),
            mask=self.video.img_ptr,
        )
