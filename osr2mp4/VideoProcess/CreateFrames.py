import ctypes
import time

import cv2

from multiprocessing import Process, Pipe
from multiprocessing.sharedctypes import RawArray
import logging
from osr2mp4.VideoProcess.Draw import draw_frame, Drawer
from osr2mp4.VideoProcess.FrameWriter import write_frame, getwriter
import os


def update_progress(framecount, deltatime, videotime):
	pass


def create_frame(settings, beatmap, replay_info, resultinfo, videotime, showranking):
	logging.debug('entering preparedframes')

	if settings.process >= 1:
		shared_array = []
		shared_pipe = []
		drawers = []
		writers = []

		start_index, end_index = videotime

		osr_interval = int((end_index - start_index) / settings.process)
		start = start_index

		my_file = open(os.path.join(settings.temp, "listvideo.txt"), "w")
		for i in range(settings.process):

			if i == settings.process - 1:
				end = end_index
			else:
				end = start + osr_interval

			shared = RawArray(ctypes.c_uint8, settings.height * settings.width * 4)
			conn1, conn2 = Pipe()

			# extract container
			_, file_extension = os.path.splitext(settings.output)
			f = "output" + str(i) + file_extension

			vid = (start, end)

			drawer = Process(target=draw_frame, args=(
				shared, conn1, beatmap, replay_info, resultinfo, vid, settings, showranking and i == settings.process-1))

			writer = Process(target=write_frame, args=(shared, conn2, settings.temp + f, settings, i == settings.process-1))

			shared_array.append(shared)
			shared_pipe.append((conn1, conn2))
			drawers.append(drawer)
			writers.append(writer)

			my_file.write("file '{}'\n".format(f))
			logging.debug("Starting process")

			drawer.start()
			logging.debug("Start drawer {}".format(i))
			writer.start()
			logging.debug("Start writer {}".format(i))

			start += osr_interval
		my_file.close()

		return drawers, writers, shared_pipe, shared_array

	else:
		from osr2mp4.VideoProcess.AFrames import PreparedFrames
		from osr2mp4.CheckSystem.mathhelper import getunstablerate
		import numpy as np

		logging.debug("process start")

		ur = getunstablerate(resultinfo)
		frames = PreparedFrames(settings, beatmap.diff, replay_info.mod_combination, ur=ur, bg=beatmap.bg, loadranking=showranking)

		shared = RawArray(ctypes.c_uint8, settings.height * settings.width * 4)
		drawer = Drawer(shared, beatmap, frames, replay_info, resultinfo, videotime, settings)

		_, file_extension = os.path.splitext(settings.output)
		f = os.path.join(settings.temp, "outputf" + file_extension)

		buf = np.zeros((settings.height * settings.width * 3), dtype=np.uint8)
		writer = getwriter(f, settings, buf)
		buf = buf.reshape((settings.height, settings.width, 3))

		logging.debug("setup done")
		framecount = 0
		startwritetime = time.time()
		while drawer.frame_info.osr_index < videotime[1]:
			status = drawer.render_draw()

			if status:
				cv2.cvtColor(drawer.np_img, cv2.COLOR_BGRA2RGB, dst=buf)

				if not settings.settings["Use FFmpeg video writer"]:
					writer.write(buf)
				else:
					writer.write()

				framecount += 1
				if framecount % 100 == 0:
					filewriter = open(os.path.join(settings.temp, "speed.txt"), "w")
					deltatime = time.time() - startwritetime
					filewriter.write("{}\n{}\n{}\n{}".format(framecount, deltatime, f, startwritetime))
					filewriter.close()

					update_progress(framecount, deltatime, videotime)

		if showranking:
			for x in range(int(5 * settings.fps)):
				drawer.draw_rankingpanel()
				im = cv2.cvtColor(drawer.np_img, cv2.COLOR_BGRA2RGB)
				writer.write(im)
		writer.release()
		logging.debug("\nprocess done")

		return None, None, None, None
