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
from skip import skip
from recordclass import recordclass

CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3

FrameInfo = recordclass("FrameInfo", "cur_time index_hitobj info_index osr_index index_fp obj_endtime x_end y_end")
CursorEvent = recordclass("CursorEvent", "event old_x old_y")


def nearer(cur_time, replay, index):
	# decide the next replay_data index, by finding the closest to the frame_info.cur_time
	min_time = abs(replay[index][TIMES] - cur_time)
	min_time_toskip = min(min_time, abs(replay[index + 1][TIMES] - cur_time))

	returnindex = 0
	key_state = replay[index][KEYS_PRESSED]
	for x in range(1, 4):
		delta_t = abs(replay[index + x][TIMES] - cur_time)
		if key_state != replay[index + x][KEYS_PRESSED]:
			if delta_t <= min_time_toskip:
				return x
		if delta_t < min_time:
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


def get_buffer(img, settings):
	np_img = np.frombuffer(img, dtype=np.uint8)
	np_img = np_img.reshape((settings.height, settings.width, 4))
	pbuffer = Image.frombuffer("RGBA", (settings.width, settings.height), np_img, 'raw', "RGBA", 0, 1)
	pbuffer.readonly = False
	return np_img, pbuffer


def render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
                preempt_followpoint, replay_event, start_index, time_preempt, updater, settings):
	if frame_info.osr_index >= start_index:
		if img.size[0] == 1:
			img = pbuffer
		np_img.fill(0)

	check_key(component, cursor_event)

	osu_d = beatmap.hitobjects[frame_info.index_hitobj]
	x_circle = int(osu_d["x"] * settings.playfieldscale) + settings.moveright
	y_circle = int(osu_d["y"] * settings.playfieldscale) + settings.movedown

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

	updater.update(frame_info.cur_time)

	cursor_x = int(cursor_event.event[CURSOR_X] * settings.playfieldscale) + settings.moveright
	cursor_y = int(cursor_event.event[CURSOR_Y] * settings.playfieldscale) + settings.movedown

	component.inputoverlayBG.add_to_frame(img, settings.width - component.inputoverlayBG.w() // 2, int(320 * settings.scale))
	component.urbar.add_to_frame_bar(img)
	component.key1.add_to_frame(img, settings.width - int(24 * settings.scale), int(350 * settings.scale))
	component.key2.add_to_frame(img, settings.width - int(24 * settings.scale), int(398 * settings.scale))
	component.mouse1.add_to_frame(img, settings.width - int(24 * settings.scale), int(446 * settings.scale))
	component.mouse2.add_to_frame(img, settings.width - int(24 * settings.scale), int(494 * settings.scale))
	component.followpoints.add_to_frame(img, frame_info.cur_time)
	component.hitobjmanager.add_to_frame(img)
	component.hitresult.add_to_frame(img)
	component.spinbonus.add_to_frame(img)
	component.combocounter.add_to_frame(img)
	component.scorecounter.add_to_frame(img, cursor_event.event[TIMES])
	component.accuracy.add_to_frame(img)
	component.urbar.add_to_frame(img)
	component.cursor_trail.add_to_frame(img, cursor_event.old_x, cursor_event.old_y)
	component.cursor.add_to_frame(img, cursor_x, cursor_y)
	component.timepie.add_to_frame(np_img, frame_info.cur_time, beatmap.end_time)

	cursor_event.old_x = cursor_x
	cursor_event.old_y = cursor_y

	frame_info.cur_time += settings.timeframe / settings.fps
	# choose correct osr index for the current time because in osr file there might be some lag
	frame_info.osr_index += nearer(frame_info.cur_time, replay_event, frame_info.osr_index)
	cursor_event.event = replay_event[frame_info.osr_index]

	return img.size[0] != 1


def setup_draw(beatmap, frames, replay_event, resultinfo, shared, skin, start_index, settings):
	old_cursor_x = int(replay_event[0][CURSOR_X] * settings.playfieldscale) + settings.moveright
	old_cursor_y = int(replay_event[0][CURSOR_Y] * settings.playfieldscale) + settings.moveright

	diffcalculator = DiffCalculator(beatmap.diff)

	time_preempt = diffcalculator.ar()

	component = FrameObjects(frames, skin, beatmap, diffcalculator, settings)

	component.cursor_trail.set_cursor(old_cursor_x, old_cursor_y)

	preempt_followpoint = 800

	updater = Updater(resultinfo, component)

	simulate = replay_event[start_index][TIMES]
	frame_info = FrameInfo(*skip(simulate, resultinfo, replay_event, beatmap.hitobjects, time_preempt, component))

	cursor_event = CursorEvent(replay_event[frame_info.osr_index], old_cursor_x, old_cursor_y)

	updater.info_index = frame_info.info_index

	img = Image.new("RGB", (1, 1))
	np_img, pbuffer = get_buffer(shared, settings)

	return component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater


def draw_frame(shared, conn, beatmap, frames, skin, replay_event, resultinfo, start_index, end_index, settings):
	asdfasdf = time.time()
	print("process start")

	component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater = setup_draw(
		beatmap, frames, replay_event, resultinfo, shared, skin, start_index, settings)
	print("setup done")
	timer = 0
	timer2 = 0
	timer3 = 0
	while frame_info.osr_index < end_index:  # len(replay_event) - 3:

		asdf = time.time()
		status = render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
		                     preempt_followpoint, replay_event, start_index, time_preempt, updater, settings)
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


def write_frame(shared, conn, filename, codec, settings):
	asdfasdf = time.time()

	writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*codec), settings.fps, (settings.width, settings.height))
	np_img = np.frombuffer(shared, dtype=np.uint8)
	np_img = np_img.reshape((settings.height, settings.width, 4))

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


def create_frame(codec, beatmap, skin, paths, replay_event, resultinfo, start_index, end_index, mpp, settings):

	diffcalculator = DiffCalculator(beatmap.diff)
	frames = PreparedFrames(skin, diffcalculator, beatmap, settings)

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

			shared = RawArray(ctypes.c_uint8, settings.height * settings.width * 4)
			conn1, conn2 = Pipe()

			# extract container
			f = paths.output[:-4] + str(i) + paths.output[-4:]

			drawer = Process(target=draw_frame, args=(
				shared, conn1, beatmap, frames, skin, replay_event, resultinfo, start, end, settings))

			writer = Process(target=write_frame, args=(shared, conn2, f, codec, settings))

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

		os.system('"{}" -safe 0 -f concat -i listvideo.txt -c copy {} -y'.format(paths.ffmpeg, paths.output))

	else:

		shared = RawArray(ctypes.c_uint8, settings.height * settings.width * 4)
		writer = cv2.VideoWriter(paths.output, cv2.VideoWriter_fourcc(*codec), settings.fps, (settings.width, settings.height))

		component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater = setup_draw(
			beatmap, frames, replay_event, resultinfo, shared, skin, start_index, settings)
		print("setup done")

		print(frame_info.osr_index, end_index)

		while frame_info.osr_index < end_index:  # len(replay_event) - 3:
			status = render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
			                     preempt_followpoint, replay_event, start_index, time_preempt, updater, settings)

			if status:
				im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
				writer.write(im)

		writer.release()
