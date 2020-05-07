import ctypes
import os
import time

import cv2

from PIL import Image
from multiprocessing import Process, Pipe
from multiprocessing.sharedctypes import RawArray
from CheckSystem.Judgement import DiffCalculator
from AFrames import *
from InfoProcessor import Updater
import numpy as np

from global_var import Settings, Paths, SkinPaths
from skip import skip
from recordclass import recordclass

CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3

FrameInfo = recordclass("FrameInfo", "cur_time index_hitobj info_index osr_index index_fp obj_endtime x_end y_end, break_index")
CursorEvent = recordclass("CursorEvent", "event old_x old_y")


def nearer(cur_time, replay, index):
	# decide the next replay_data index, by finding the closest to the frame_info.cur_time
	min_time = abs(replay[index][TIMES] - cur_time)
	min_time_toskip = min(min_time, abs(replay[index + 1][TIMES] - cur_time))

	returnindex = 0
	key_state = replay[index][KEYS_PRESSED]
	end = min(10, len(replay) - index - 1)
	for x in range(0, end):
		delta_t = abs(replay[index + x][TIMES] - cur_time)
		# if key_state != replay[index + x][KEYS_PRESSED]:
		# 	if delta_t <= min_time_toskip:
		# 		return x
		if delta_t <= min_time:
			min_time = delta_t
			returnindex = x

	return returnindex


def find_followp_target(beatmap, frame_info):
	# reminder: index means the previous circle. the followpoints will point to the circle of index+1

	index = frame_info.index_fp

	while "spinner" in beatmap.hitobjects[index + 1]["type"] or "new combo" in beatmap.hitobjects[index + 1]["type"]:
		index += 1

	if "end" in beatmap.hitobjects[index + 1]["type"]:
		frame_info.x_end = 0
		frame_info.y_end = 0

		frame_info.obj_endtime = beatmap.hitobjects[index]["end time"] * 10
		frame_info.index_fp = index * 10
		return index * 10, beatmap.hitobjects[index]["end time"] * 10, 0, 0

	osu_d = beatmap.hitobjects[index]
	frame_info.x_end = osu_d["end x"]
	frame_info.y_end = osu_d["end y"]

	frame_info.obj_endtime = osu_d["end time"]
	frame_info.index_fp = index


def keys(n):
	k1 = n & 5 == 5
	k2 = n & 10 == 10
	m1 = not k1 and n & 1 == 1
	m2 = not k2 and n & 2 == 2
	smoke = n & 16 == 16
	return k1, k2, m1, m2  # fuck smoke


def check_key(component, cursor_event):
	k1, k2, m1, m2 = keys(cursor_event.event[KEYS_PRESSED])
	if k1:
		component.key1.clicked(cursor_event.event[TIMES])
	if k2:
		component.key2.clicked(cursor_event.event[TIMES])
	if m1:
		component.mouse1.clicked(cursor_event.event[TIMES])
	if m2:
		component.mouse2.clicked(cursor_event.event[TIMES])


def get_buffer(img):
	np_img = np.frombuffer(img, dtype=np.uint8)
	np_img = np_img.reshape((Settings.height, Settings.width, 4))
	pbuffer = Image.frombuffer("RGBA", (Settings.width, Settings.height), np_img, 'raw', "RGBA", 0, 1)
	pbuffer.readonly = False
	return np_img, pbuffer


def render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
                preempt_followpoint, replay_event, start_index, time_preempt, updater):

	breakperiod = beatmap.breakperiods[frame_info.break_index]
	next_break = frame_info.cur_time > breakperiod["End"]
	if next_break:
		frame_info.break_index = min(frame_info.break_index+1, len(beatmap.breakperiods)-1)
		component.background.startbreak(beatmap.breakperiods[frame_info.break_index], frame_info.cur_time)
		breakperiod = beatmap.breakperiods[frame_info.break_index]

	in_break = int(frame_info.cur_time) in range(breakperiod["Start"], breakperiod["End"])
	# print(breakperiod, frame_info.cur_time, in_break)

	if frame_info.osr_index >= start_index:
		if img.size[0] == 1:
			img = pbuffer
		# if not in_break:
		# 	# np_img.fill(0)
		# 	img.paste((0, 0, 0, 255), (0, 0, img.size[0], img.size[1]))

	component.background.add_to_frame(img, np_img, frame_info.cur_time)

	if not in_break:
		check_key(component, cursor_event)

	osu_d = beatmap.hitobjects[frame_info.index_hitobj]
	x_circle = int(osu_d["x"] * Settings.playfieldscale) + Settings.moveright
	y_circle = int(osu_d["y"] * Settings.playfieldscale) + Settings.movedown

	# check if it's time to draw followpoints
	if frame_info.cur_time + preempt_followpoint >= frame_info.obj_endtime and frame_info.index_fp + 2 < len(
			beatmap.hitobjects):
		frame_info.index_fp += 1

		component.followpoints.add_fp(frame_info.x_end, frame_info.y_end, frame_info.obj_endtime,
		                              beatmap.hitobjects[frame_info.index_fp])

		find_followp_target(beatmap, frame_info)

	# check if it's time to draw circles
	if frame_info.cur_time + time_preempt >= osu_d["time"] and frame_info.index_hitobj + 1 < len(beatmap.hitobjects):

		if "spinner" in osu_d["type"]:

			if frame_info.cur_time + 400 > osu_d["time"]:
				component.hitobjmanager.add_spinner(osu_d["time"], osu_d["end time"], frame_info.cur_time)
				frame_info.index_hitobj += 1

		else:

			component.hitobjmanager.add_circle(x_circle, y_circle, frame_info.cur_time, osu_d)

			if "slider" in osu_d["type"]:
				component.hitobjmanager.add_slider(osu_d, x_circle, y_circle, frame_info.cur_time)

			frame_info.index_hitobj += 1

	half = breakperiod["Start"] + (breakperiod["End"] - breakperiod["Start"])/2
	if frame_info.cur_time > half and breakperiod["End"] - breakperiod["Start"] > 2000:
		component.sections.startbreak(1, breakperiod["Start"])

	if in_break:
		component.scorebar.startbreak(breakperiod["Start"], breakperiod["End"] - frame_info.cur_time)

	updater.update(frame_info.cur_time)

	cursor_x = int(cursor_event.event[CURSOR_X] * Settings.playfieldscale) + Settings.moveright
	cursor_y = int(cursor_event.event[CURSOR_Y] * Settings.playfieldscale) + Settings.movedown

	component.scorebar.add_to_frame(img)
	component.inputoverlayBG.add_to_frame(img, Settings.width - component.inputoverlayBG.w() // 2, int(320 * Settings.scale))
	component.urbar.add_to_frame_bar(img)
	component.key1.add_to_frame(img, Settings.width - int(24 * Settings.scale), int(350 * Settings.scale))
	component.key2.add_to_frame(img, Settings.width - int(24 * Settings.scale), int(398 * Settings.scale))
	component.mouse1.add_to_frame(img, Settings.width - int(24 * Settings.scale), int(446 * Settings.scale))
	component.mouse2.add_to_frame(img, Settings.width - int(24 * Settings.scale), int(494 * Settings.scale))
	component.followpoints.add_to_frame(img, frame_info.cur_time)
	component.hitobjmanager.add_to_frame(img)
	component.hitresult.add_to_frame(img)
	component.spinbonus.add_to_frame(img)
	component.combocounter.add_to_frame(img)
	component.scorecounter.add_to_frame(img, cursor_event.event[TIMES])
	component.accuracy.add_to_frame(img)
	component.urbar.add_to_frame(img)
	component.cursor_trail.add_to_frame(img, cursor_x, cursor_y)
	component.cursor.add_to_frame(img, cursor_x, cursor_y)
	component.cursormiddle.add_to_frame(img, cursor_x, cursor_y)
	component.sections.add_to_frame(img)
	component.timepie.add_to_frame(np_img, frame_info.cur_time, beatmap.end_time)

	cursor_event.old_x = cursor_x
	cursor_event.old_y = cursor_y

	frame_info.cur_time += Settings.timeframe / Settings.fps

	# choose correct osr index for the current time because in osr file there might be some lag
	frame_info.osr_index += nearer(frame_info.cur_time, replay_event, frame_info.osr_index)
	cursor_event.event = replay_event[frame_info.osr_index]
	return img.size[0] != 1


def setup_draw(beatmap, frames, replay_event, resultinfo, shared, skin, start_index, hd):
	old_cursor_x = int(replay_event[0][CURSOR_X] * Settings.playfieldscale) + Settings.moveright
	old_cursor_y = int(replay_event[0][CURSOR_Y] * Settings.playfieldscale) + Settings.moveright

	diffcalculator = DiffCalculator(beatmap.diff)

	time_preempt = diffcalculator.ar()

	component = FrameObjects(frames, skin, beatmap, diffcalculator, hd)

	component.cursor_trail.set_cursor(old_cursor_x, old_cursor_y)

	preempt_followpoint = 800

	updater = Updater(resultinfo, component)

	simulate = replay_event[start_index][TIMES]
	frame_info = FrameInfo(*skip(simulate, resultinfo, replay_event, beatmap, time_preempt, component))

	print(start_index, frame_info.osr_index)
	component.background.startbreak(beatmap.breakperiods[frame_info.break_index], frame_info.cur_time)

	cursor_event = CursorEvent(replay_event[frame_info.osr_index], old_cursor_x, old_cursor_y)

	updater.info_index = frame_info.info_index

	img = Image.new("RGB", (1, 1))
	np_img, pbuffer = get_buffer(shared)


	return component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater


def setup_global(settings, paths, skinpaths):
	Settings.width, Settings.height, Settings.scale = settings[0], settings[1], settings[2]
	Settings.playfieldscale, Settings.playfieldwidth, Settings.playfieldheight = settings[3], settings[4], settings[5]
	Settings.fps, Settings.timeframe = settings[6], settings[7]
	Settings.moveright, Settings.movedown = settings[8], settings[9]

	SkinPaths.path = skinpaths[0]
	SkinPaths.default_path = skinpaths[1]
	SkinPaths.skin_ini = skinpaths[2]
	SkinPaths.default_skin_ini = skinpaths[3]

	Paths.output = paths[0]
	Paths.ffmpeg = paths[1]
	Paths.beatmap = paths[2]


def draw_frame(shared, conn, beatmap, frames, skin, replay_event, resultinfo, start_index, end_index, hd, settings, paths, skinpaths):
	asdfasdf = time.time()
	print("process start")

	setup_global(settings, paths, skinpaths)

	component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater = setup_draw(
		beatmap, frames, replay_event, resultinfo, shared, skin, start_index, hd)
	print("setup done")
	timer = 0
	timer2 = 0
	timer3 = 0
	while frame_info.osr_index < end_index:

		asdf = time.time()
		status = render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
		                     preempt_followpoint, replay_event, start_index, time_preempt, updater)
		timer += time.time() - asdf

		asdf = time.time()
		if status:
			# print("send")
			conn.send(1)
			# print("sent")
			timer3 += time.time() - asdf

			asdf = time.time()
			# print("wait")
			i = conn.recv()
			# print("received")
			timer2 += time.time() - asdf
		# print("unlocked", timer2)

	conn.send(10)
	print("\nprocess done")
	print("Drawing time:", timer)
	print("Total time:", time.time() - asdfasdf)
	print("Waiting time:", timer2)
	print("Changing value time:", timer3)




def write_frame(shared, conn, filename, codec, settings, paths, skinpaths):
	asdfasdf = time.time()

	setup_global(settings, paths, skinpaths)

	writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*codec), Settings.fps, (Settings.width, Settings.height))
	np_img = np.frombuffer(shared, dtype=np.uint8)
	np_img = np_img.reshape((Settings.height, Settings.width, 4))

	timer = 0

	timer2 = 0
	timer3 = 0
	timer4 = 0
	a = 0
	print("start writing:", time.time() - asdfasdf)

	while a != 10:

		asdf = time.time()
		# print("video wait")
		# print(filename)
		a = conn.recv()
		# print("video received")
		timer2 += time.time() - asdf

		if a == 1:

			asdf = time.time()
			im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
			# print("video send")
			conn.send(0)
			# print("video sent")
			timer3 += time.time() - asdf
			# print("unlock", timer3)

			asdf = time.time()
			writer.write(im)
			timer += time.time() - asdf

	writer.release()
	print("\nWriting time:", timer)

	print("\nTotal time:", time.time() - asdfasdf)
	print("Writing time:", timer)
	print("Waiting time:", timer2)
	print("Changing value time:", timer3)
	print("??? value time:", timer4)


def getlist():
	settings = []
	paths = []
	skinpaths = []

	settings.extend([Settings.width, Settings.height, Settings.scale])
	settings.extend([Settings.playfieldscale, Settings.playfieldwidth, Settings.playfieldheight])
	settings.extend([Settings.fps, Settings.timeframe])
	settings.extend([Settings.moveright, Settings.movedown])

	skinpaths.append(SkinPaths.path)
	skinpaths.append(SkinPaths.default_path)
	skinpaths.append(SkinPaths.skin_ini)
	skinpaths.append(SkinPaths.default_skin_ini)

	paths.append(Paths.output)
	paths.append(Paths.ffmpeg)
	paths.append(Paths.beatmap)

	return settings, paths, skinpaths


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

		for i in range(mpp):
			drawers[i].join()
			conn1, conn2 = shared_pipe[i]
			conn1.close()
			conn2.close()
			writers[i].join()
		f = Paths.output[:-4] + "f" + Paths.output[-4:]
		os.system('"{}" -safe 0 -f concat -i listvideo.txt -c copy \'{}\' -y'.format(Paths.ffmpeg, f))

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
