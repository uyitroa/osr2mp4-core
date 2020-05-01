import ctypes
import os
import time

import cv2

from PIL import Image
from multiprocessing import Process, Array, Value
from ImageProcess.Objects.Components.Followpoints import FollowPointsManager
from ImageProcess.Objects.Components.TimePie import TimePie
from ImageProcess.Objects.HitObjects.CircleNumber import Number
from ImageProcess.Objects.HitObjects.Slider import SliderManager
from ImageProcess.Objects.HitObjects.Spinner import SpinnerManager
from ImageProcess.Objects.Scores.Accuracy import Accuracy
from ImageProcess.Objects.Scores.ComboCounter import ComboCounter
from ImageProcess.Objects.Scores.Hitresult import HitResult
from ImageProcess.Objects.Scores.ScoreCounter import ScoreCounter
from ImageProcess.Objects.Scores.ScoreNumbers import ScoreNumbers
from ImageProcess.Objects.HitObjects.Circles import CircleManager
from ImageProcess.Objects.HitObjects.Manager import HitObjectManager
from ImageProcess.Objects.Components.Button import InputOverlay, InputOverlayBG, ScoreEntry
from ImageProcess.Objects.Components.Cursor import Cursor, Cursortrail
from ImageProcess.Objects.Scores.SpinBonusScore import SpinBonusScore
from ImageProcess.Objects.Scores.URBar import URBar
from CheckSystem.Judgement import DiffCalculator
from ImageProcess.PrepareFrames.Components.Button import prepare_scoreentry, prepare_inputoverlaybg, \
	prepare_inputoverlay
from ImageProcess.PrepareFrames.Components.Cursor import prepare_cursor, prepare_cursortrail
from ImageProcess.PrepareFrames.Components.Followpoints import prepare_fpmanager
from ImageProcess.PrepareFrames.HitObjects.CircleNumber import prepare_hitcirclenumber
from ImageProcess.PrepareFrames.HitObjects.Circles import prepare_circle, calculate_ar
from ImageProcess.PrepareFrames.HitObjects.Slider import prepare_slider
from ImageProcess.PrepareFrames.HitObjects.Spinner import prepare_spinner
from ImageProcess.PrepareFrames.Scores.Accuracy import prepare_accuracy
from ImageProcess.PrepareFrames.Scores.ComboCounter import prepare_combo
from ImageProcess.PrepareFrames.Scores.Hitresult import prepare_hitresults
from ImageProcess.PrepareFrames.Scores.ScoreCounter import prepare_scorecounter
from ImageProcess.PrepareFrames.Scores.SpinBonusScore import prepare_spinbonus
from ImageProcess.PrepareFrames.Scores.URBar import prepare_bar
from InfoProcessor import Updater
import numpy as np
from skip import skip
from recordclass import recordclass

CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3

WIDTH = 1920
HEIGHT = 1080
FPS = 60
PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8  # actual playfield is smaller than screen res
PLAYFIELD_SCALE = PLAYFIELD_WIDTH / 512
SCALE = HEIGHT / 768
MOVE_RIGHT = int(WIDTH * 0.2)  # center the playfield
MOVE_DOWN = int(HEIGHT * 0.1)

FrameInfo = recordclass("FrameInfo", "cur_time index_hitobj info_index osr_index index_fp obj_endtime x_end y_end")
Settings = recordclass("Settings", "width height fps scale playfieldscale movedown moveright")
CursorEvent = recordclass("CursorEvent", "event old_x old_y")

settings = Settings(WIDTH, HEIGHT, FPS, SCALE, PLAYFIELD_SCALE, MOVE_DOWN, MOVE_RIGHT)


class PreparedFrames:
	def __init__(self, path, skin, check, beatmap):
		self.cursor = prepare_cursor(path, SCALE)
		self.cursor_trail = prepare_cursortrail(path, SCALE)
		self.scoreentry = prepare_scoreentry(path, SCALE, skin.colours["InputOverlayText"])
		self.inputoverlayBG = prepare_inputoverlaybg(path, SCALE)
		self.key = prepare_inputoverlay(path, SCALE, [255, 255, 0])
		self.mouse = prepare_inputoverlay(path, SCALE, [255, 0, 255])
		self.scorenumbers = ScoreNumbers(skin.fonts, path, SCALE)
		self.hitcirclenumber = prepare_hitcirclenumber(path, skin.fonts, beatmap.diff, PLAYFIELD_SCALE)
		self.accuracy = prepare_accuracy(self.scorenumbers)
		self.combocounter = prepare_combo(self.scorenumbers)
		self.hitresult = prepare_hitresults(path, SCALE)
		self.spinbonus = prepare_spinbonus(self.scorenumbers)
		self.scorecounter = prepare_scorecounter(self.scorenumbers)
		self.urbar = prepare_bar(SCALE, check.scorewindow)
		self.fpmanager = prepare_fpmanager(path, PLAYFIELD_SCALE)
		self.circle = prepare_circle(beatmap, path, PLAYFIELD_SCALE, skin, FPS)
		self.slider = prepare_slider(path, beatmap.diff, PLAYFIELD_SCALE, skin, FPS)
		self.spinner = prepare_spinner(path, PLAYFIELD_SCALE)


class FrameObjects:
	def __init__(self, frames, skin, beatmap, check):
		opacity_interval, timepreempt, _ = calculate_ar(beatmap.diff["ApproachRate"], FPS)

		self.cursor = Cursor(frames.cursor)
		self.cursor_trail = Cursortrail(frames.cursor_trail)
		# self.lifegraph = LifeGraph(skin_path + "scorebar-colour")

		self.scoreentry = ScoreEntry(frames.scoreentry)

		self.inputoverlayBG = InputOverlayBG(frames.inputoverlayBG)
		self.key1 = InputOverlay(frames.key, self.scoreentry)
		self.key2 = InputOverlay(frames.key, self.scoreentry)
		self.mouse1 = InputOverlay(frames.mouse, self.scoreentry)
		self.mouse2 = InputOverlay(frames.mouse, self.scoreentry)

		self.accuracy = Accuracy(frames.accuracy, skin.fonts["ScoreOverlap"], settings)
		self.timepie = TimePie(SCALE, self.accuracy)
		self.hitresult = HitResult(frames.hitresult, settings)
		self.spinbonus = SpinBonusScore(frames.spinbonus, skin.fonts["ScoreOverlap"], settings)
		self.combocounter = ComboCounter(frames.combocounter, skin.fonts["ScoreOverlap"], settings)
		self.scorecounter = ScoreCounter(frames.scorecounter, beatmap.diff, skin.fonts["ScoreOverlap"], settings)

		self.urbar = URBar(frames.urbar, settings)

		self.followpoints = FollowPointsManager(frames.fpmanager, settings)

		self.hitcirclenumber = Number(frames.hitcirclenumber, skin.fonts, opacity_interval)
		self.circle = CircleManager(frames.circle, timepreempt, self.hitcirclenumber)
		self.slider = SliderManager(frames.slider, beatmap.diff, skin, settings)
		self.spinner = SpinnerManager(frames.spinner, settings)
		self.hitobjmanager = HitObjectManager(self.circle, self.slider, self.spinner, check.scorewindow[2])


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


def get_buffer(img):
	np_img = np.frombuffer(img.get_obj(), dtype=np.uint8)
	np_img = np_img.reshape((HEIGHT, WIDTH, 4))
	pbuffer = Image.frombuffer("RGBA", (WIDTH, HEIGHT), np_img, 'raw', "RGBA", 0, 1)
	pbuffer.readonly = False
	return np_img, pbuffer


def render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
                preempt_followpoint, replay_event, start_index, time_preempt, updater):
	if frame_info.osr_index >= start_index:
		if img.size[0] == 1:
			img = pbuffer
		np_img.fill(0)

	check_key(component, cursor_event)

	osu_d = beatmap.hitobjects[frame_info.index_hitobj]
	x_circle = int(osu_d["x"] * PLAYFIELD_SCALE) + MOVE_RIGHT
	y_circle = int(osu_d["y"] * PLAYFIELD_SCALE) + MOVE_DOWN

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

	cursor_x = int(cursor_event.event[CURSOR_X] * PLAYFIELD_SCALE) + MOVE_RIGHT
	cursor_y = int(cursor_event.event[CURSOR_Y] * PLAYFIELD_SCALE) + MOVE_DOWN

	component.inputoverlayBG.add_to_frame(img, WIDTH - component.inputoverlayBG.w() // 2, int(320 * SCALE))
	component.urbar.add_to_frame_bar(img)
	component.key1.add_to_frame(img, WIDTH - int(24 * SCALE), int(350 * SCALE))
	component.key2.add_to_frame(img, WIDTH - int(24 * SCALE), int(398 * SCALE))
	component.mouse1.add_to_frame(img, WIDTH - int(24 * SCALE), int(446 * SCALE))
	component.mouse2.add_to_frame(img, WIDTH - int(24 * SCALE), int(494 * SCALE))
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

	frame_info.cur_time += 1000 / FPS
	# choose correct osr index for the current time because in osr file there might be some lag
	frame_info.osr_index += nearer(frame_info.cur_time, replay_event, frame_info.osr_index)
	cursor_event.event = replay_event[frame_info.osr_index]

	return img.size[0] != 1


def setup_draw(beatmap, replay_event, resultinfo, shared, skin, skin_path, start_index):
	old_cursor_x = int(replay_event[0][CURSOR_X] * PLAYFIELD_SCALE) + MOVE_RIGHT
	old_cursor_y = int(replay_event[0][CURSOR_Y] * PLAYFIELD_SCALE) + MOVE_RIGHT
	diffcalculator = DiffCalculator(beatmap.diff)
	time_preempt = diffcalculator.ar()
	frames = PreparedFrames(skin_path, skin, diffcalculator, beatmap)
	component = FrameObjects(frames, skin, beatmap, diffcalculator)
	component.cursor_trail.set_cursor(old_cursor_x, old_cursor_y)
	preempt_followpoint = 800
	updater = Updater(resultinfo, component)
	simulate = replay_event[start_index][TIMES]
	frame_info = FrameInfo(*skip(simulate, resultinfo, replay_event, beatmap.hitobjects, time_preempt, component))
	cursor_event = CursorEvent(replay_event[frame_info.osr_index], old_cursor_x, old_cursor_y)
	updater.info_index = frame_info.info_index
	img = Image.new("RGB", (1, 1))
	np_img, pbuffer = get_buffer(shared)
	return component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater


def draw_frame(shared, lock, beatmap, skin, skin_path, replay_event, resultinfo, start_index, end_index):
	print("process start")

	component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater = setup_draw(
		beatmap, replay_event, resultinfo, shared, skin, skin_path, start_index)
	print("setup done")
	timer = 0
	while frame_info.osr_index < end_index:  # len(replay_event) - 3:
		asdf = time.time()
		status = render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
		                     preempt_followpoint, replay_event, start_index, time_preempt, updater)
		timer += time.time() - asdf
		if status:
			lock.value = 1

		while lock.value == 1:
			pass

	lock.value = 10
	print("process done")
	print("\nDrawing time:", timer)


def write_frame(shared, lock, filename, codec):
	writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*codec), FPS, (WIDTH, HEIGHT))
	np_img = np.frombuffer(shared.get_obj(), dtype=np.uint8)
	np_img = np_img.reshape((HEIGHT, WIDTH, 4))

	timer = 0

	while lock.value != 10:
		if lock.value == 1:
			asdf = time.time()
			im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
			lock.value = 0
			writer.write(im)
			timer += time.time() - asdf

	writer.release()
	print("\nWriting time:", timer)


def create_frame(filename, codec, beatmap, skin, skin_path, replay_event, resultinfo, start_index, end_index, mpp):
	if mpp > 1:
		shared_array = []
		shared_lock = []
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

			shared = Array(ctypes.c_uint8, HEIGHT * WIDTH * 4)
			lock = Value('i', 0)

			f = str(i) + filename

			drawer = Process(target=draw_frame, args=(
				shared, lock, beatmap, skin, skin_path, replay_event, resultinfo, start, end,))
			writer = Process(target=write_frame, args=(shared, lock, f, codec,))

			shared_array.append(shared)
			shared_lock.append(lock)
			drawers.append(drawer)
			writers.append(writer)

			my_file.write("file '{}'\n".format(f))

			drawer.start()
			writer.start()

			start += osr_interval

		my_file.close()

		for i in range(mpp):
			drawers[i].join()
			shared_lock[i].value = 10
			writers[i].join()

		os.system("ffmpeg -safe 0 -f concat -i listvideo.txt -c copy {} -y".format(filename))

	else:
		shared = Array(ctypes.c_uint8, HEIGHT * WIDTH * 4)
		writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*codec), FPS, (WIDTH, HEIGHT))
		component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater = setup_draw(
			beatmap, replay_event, resultinfo, shared, skin, skin_path, start_index)
		print("setup done")

		while frame_info.osr_index < end_index:  # len(replay_event) - 3:
			status = render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
			                     preempt_followpoint, replay_event, start_index, time_preempt, updater)

			if status:
				im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
				writer.write(im)

		writer.release()
