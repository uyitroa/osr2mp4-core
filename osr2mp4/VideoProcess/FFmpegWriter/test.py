from osr2mp4cv import PyFrameWriter
import ctypes
import numpy as np
from multiprocessing.sharedctypes import RawArray

width, height = 1920, 1080

shared = RawArray(ctypes.c_uint8, height * width * 4)

nparr = np.frombuffer(shared, dtype=np.uint8)
a = PyFrameWriter(b"ok.mp4", b"libx264", 60, width, height, b"-preset ultrafast -crf 23", nparr)
af = nparr.reshape((height, width, 4))
for i in range(600):
	x = i % 1070
	af[x:x+10, x:x+10, :] = 255
	a.write_frame()
	af[x:x+10, x:x+10, :] = 0
a.close_video()
