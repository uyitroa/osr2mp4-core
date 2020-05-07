import ctypes
import cv2

from multiprocessing import Process, Pipe
from multiprocessing.sharedctypes import RawArray
from CheckSystem.Judgement import DiffCalculator
from VideoProcess.AFrames import *
from VideoProcess.Draw import draw_frame, render_draw
from VideoProcess.FrameWriter import write_frame
from VideoProcess.Setup import getlist, setup_draw

from global_var import Settings, Paths

CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3



def create_frame(codec, beatmap, skin, replay_event, resultinfo, start_index, end_index, mpp, hd):

	diffcalculator = DiffCalculator(beatmap.diff)
	frames = PreparedFrames(skin, diffcalculator, beatmap, hd)

	if mpp >= 1:
		shared_array = []
		shared_pipe = []
		drawers = []
		writers = []

		osr_interval = int((end_index - start_index) / mpp)
		start = start_index

		my_file = open("listvideo.txt", "w")
		for i in range(mpp):

			if i == mpp - 1:
				end = end_index
			else:
				end = start + osr_interval

			shared = RawArray(ctypes.c_uint8, Settings.height * Settings.width * 4)
			conn1, conn2 = Pipe()

			# extract container
			f = Paths.output[:-4] + str(i) + Paths.output[-4:]

			globalvars = getlist()

			drawer = Process(target=draw_frame, args=(
				shared, conn1, beatmap, frames, skin, replay_event, resultinfo, start, end, hd, *globalvars))

			writer = Process(target=write_frame, args=(shared, conn2, f, codec, *globalvars))

			shared_array.append(shared)
			shared_pipe.append((conn1, conn2))
			drawers.append(drawer)
			writers.append(writer)

			my_file.write("file '{}'\n".format(f))

			drawer.start()
			writer.start()

			start += osr_interval
		my_file.close()

		return drawers, writers, shared_pipe


	else:
		f = Paths.output[:-4] + "f" + Paths.output[-4:]
		shared = RawArray(ctypes.c_uint8, Settings.height * Settings.width * 4)
		writer = cv2.VideoWriter(f, cv2.VideoWriter_fourcc(*codec), Settings.fps, (Settings.width, Settings.height))

		component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater = setup_draw(
			beatmap, frames, replay_event, resultinfo, shared, skin, start_index, hd)
		print("setup done")

		print(frame_info.osr_index, end_index)

		while frame_info.osr_index < end_index:  # len(replay_event) - 3:
			status = render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
			                     preempt_followpoint, replay_event, start_index, time_preempt, updater)
			cv2.putText(np_img, str(replay_event[frame_info.osr_index][TIMES]), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255, 255), 2)
			if status:
				im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
				writer.write(im)

		writer.release()
		return None
