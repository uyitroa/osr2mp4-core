import ctypes
import cv2

from multiprocessing import Process, Pipe
from multiprocessing.sharedctypes import RawArray
from ..CheckSystem.Judgement import DiffCalculator
from .AFrames import *
from .Draw import draw_frame, render_draw
from .FrameWriter import write_frame
from .Setup import getlist, setup_draw
from ..global_var import Settings, Paths, GameplaySettings


def create_frame(codec, beatmap, skin, replay_event, replay_info, resultinfo, start_index, end_index, mpp, hd, showranking):

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
			f = Paths.path + "temp/output" + str(i) + Paths.output[-4:]

			globalvars = getlist()

			drawer = Process(target=draw_frame, args=(
				shared, conn1, beatmap, frames, skin, replay_event, replay_info, resultinfo, start, end, hd, *globalvars, GameplaySettings.settings, showranking and i == mpp-1))

			writer = Process(target=write_frame, args=(shared, conn2, f, codec, *globalvars, GameplaySettings.settings))

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
		f = Paths.path + "temp/outputf" + Paths.output[-4:]
		shared = RawArray(ctypes.c_uint8, Settings.height * Settings.width * 4)
		writer = cv2.VideoWriter(f, cv2.VideoWriter_fourcc(*codec), Settings.fps, (Settings.width, Settings.height))

		component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater = setup_draw(
			beatmap, frames, replay_event, replay_info, resultinfo, shared, skin, start_index, hd)
		print("setup done")

		print(frame_info.osr_index, end_index)

		counter = 0
		while frame_info.osr_index < end_index:  # len(replay_event) - 3:
			status = render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
			                     preempt_followpoint, replay_event, start_index, time_preempt, updater)

			if status:
				im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
				writer.write(im)
				# if counter > 0:
				# 	counter -= 1
				# 	print(counter)
				# 	continue
				# im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
				# # writer.write(im)
				# cv2.imshow("debug", im)
				# cv2.waitKey(0)
				#
				# a = ""
				# while "next" not in a and a != "stop":
				# 	a = input(">> ")
				# 	try:
				# 		exec(a)
				# 	except Exception as e:
				# 		print(e)
				# if a == "stop":
				# 	break
				# if a != "next" and "next" in a:
				# 	counter = int(a[5:])

		if showranking:
			component.rankingpanel.start_show()
			component.rankinghitresults.start_show()
			component.rankingtitle.start_show()
			component.rankingcombo.start_show()
			component.rankingaccuracy.start_show()
			component.rankinggrade.start_show()
			component.menuback.start_show()
			component.modicons.start_show()
			component.rankingreplay.start_show()
			component.rankinggraph.start_show()
			for x in range(200):
				# np_img.fill(0)
				component.rankingpanel.add_to_frame(pbuffer)
				component.rankinghitresults.add_to_frame(pbuffer)
				component.rankingtitle.add_to_frame(pbuffer, np_img)
				component.rankingcombo.add_to_frame(pbuffer)
				component.rankingaccuracy.add_to_frame(pbuffer)
				component.rankinggrade.add_to_frame(pbuffer)
				component.menuback.add_to_frame(pbuffer)
				component.modicons.add_to_frame(pbuffer)
				component.rankingreplay.add_to_frame(pbuffer)
				component.rankinggraph.add_to_frame(pbuffer)

				im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
				writer.write(im)

		writer.release()
		return None, None, None
