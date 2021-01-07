import ctypes
import time

import cv2

from multiprocessing import Process, Pipe
from osr2mp4 import logger
from osr2mp4.VideoProcess.Draw import draw_frame, Drawer
from osr2mp4.VideoProcess.FrameWriter import getwriter
import os

def create_frame(settings, beatmap, replay_info, resultinfo, videotime):
	logger.debug('entering preparedframes')
	
	from osr2mp4.VideoProcess.AFrames import PreparedFrames
	from osr2mp4.CheckSystem.mathhelper import getunstablerate
	import numpy as np

	logger.debug("process start")

	ur = getunstablerate(resultinfo)
	frames = PreparedFrames(settings, beatmap.diff, replay_info.mod_combination, ur=ur, bg=beatmap.bg)

	shared = np.zeros((settings.height * settings.width * 4), dtype=np.uint8)
	drawer = Drawer(shared, beatmap, frames, replay_info, resultinfo, videotime, settings)

	_, file_extension = os.path.splitext(settings.output)
	f = os.path.join(settings.temp, "outputf" + file_extension)

	writer = getwriter(f, settings)
	buf = np.zeros((settings.height + int(settings.height/2.0), settings.width), dtype=np.uint8)

	logger.debug("setup done")
	startwritetime = time.time()
	while drawer.frame_info.osr_index < videotime[1]:
		status = drawer.render_draw()
		if status:
			cv2.cvtColor(drawer.np_img, cv2.COLOR_BGRA2YUV_YV12, dst=buf)
			writer.write_frame(buf)

	writer.release()
	logger.debug("\nprocess done")

	return None, None, None, None
