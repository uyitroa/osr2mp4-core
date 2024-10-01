"""

    why is it so not poggers to code this shit

"""
import subprocess
import ctypes
import numpy as np
import cv2
from PIL import Image
from pathlib import Path
from multiprocessing.sharedctypes import RawArray

class VideoBuffer:
    def __init__(self, path: Path, ffmpeg_path: Path) -> None:
        self.path: str = path
        self.pipe: subprocess.Popen = None
        self.running: bool = False
        self.ffmpeg = ffmpeg_path

        # metadata
        self.end_resolution: list = None
        self.width: int = 0
        self.height: int = 0
        self.fps: int = 0

        # buffer
        self.buffer: RawArray = None
        self.np_buffer: np.array = None
        self.img_ptr: Image.Image = None
        


    def start(self, time: int = 0) -> None:
        if self.running:
            return

        args: list = [
            str(self.ffmpeg), '-i', str(self.path),
            '-f', 'rawvideo', '-pix_fmt', 
            'rgb24', '-ss', f'{int(time/1000)}.{time%1000}', '-'
        ]
        self.pipe = subprocess.Popen(args, stdout=subprocess.PIPE, shell=False)
        self.running = True

    def update(self) -> None:
        raw_image = self.pipe.stdout.read(self.height * self.width * 3) # i hope theres no video format that has 4 channels cuz thats stupid

        if len(raw_image) < (self.height * self.width * 3):
            self.running = False
            return

        raw_buffer = np.frombuffer(raw_image, dtype=np.uint8).reshape((self.height, self.width, 3)) # why is it always swapped ???
        raw_buffer = cv2.cvtColor(raw_buffer, cv2.COLOR_RGB2RGBA)

        # update da buffer
        self.np_buffer[0:] = cv2.resize(raw_buffer, dsize=self.end_resolution)

    @classmethod
    def from_file(cls: object, filepath: str, target_resolution: list, ffmpeg_path: Path) -> object:
        filepath = Path(filepath)

        if not filepath.exists():
            raise Exception('Video file not existed, returning.')

        cv2_video = cv2.VideoCapture(str(filepath))
        video = cls(filepath, ffmpeg_path)

        # metadata shit
        video.width = int(cv2_video.get(cv2.CAP_PROP_FRAME_WIDTH))
        video.height = int(cv2_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video.fps = cv2_video.get(cv2.CAP_PROP_FPS)

        # some bullshit ratio deez nuts stuff. pretty sure its not 1:1 with whatever the fuck osu uses.
        ratio = target_resolution[0] / video.width
        target_resolution = [
            int(video.width * ratio),
            int(video.height * ratio)
        ]
        video.end_resolution = target_resolution


        # got damn buffer stuff
        video.buffer = RawArray(ctypes.c_uint8, video.end_resolution[0] * video.end_resolution[1] * 4) # ...yea
        video.np_buffer = np.frombuffer(video.buffer, dtype=np.uint8)
        video.np_buffer = video.np_buffer.reshape((video.end_resolution[1], video.end_resolution[0], 4))
        video.img_ptr = Image.frombuffer('RGBA', (video.end_resolution[0], video.end_resolution[1]), video.np_buffer, 'raw', 'RGBA', 0, 1)
        video.img_ptr.readonly = False

        return video