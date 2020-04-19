import cv2
import time

from PIL import Image

from Objects.Component.Playfield import Playfield
from Objects.HitObjects.PrepareHitObjFrames import PrepareCircles, PrepareSlider, PrepareSpinner, Timer
from Objects.HitObjects.Slider import SliderManager
from Objects.HitObjects.Spinner import SpinnerManager
from Objects.Scores.Accuracy import Accuracy
# from Objects.Scores.ComboCounter import ComboCounter
# from Objects.Scores.Hitresult import HitResult
from Objects.Scores.ScoreCounter import ScoreCounter
from Objects.Scores.ScoreNumbers import ScoreNumbers
# from Objects.Scores.SpinBonusScore import SpinBonusScore
# from Objects.Scores.URBar import URBar
# from Objects.Component.TimePie import TimePie
# from Objects.Component.Followpoints import FollowPointsManager
from Objects.HitObjects.Circles import CircleManager
from Objects.HitObjects.Manager import HitObjectManager
from Objects.Component.Button import InputOverlay, InputOverlayBG, ScoreEntry
from Objects.Component.Cursor import Cursor, Cursortrail
from Objects.Component.LifeGraph import LifeGraph
from CheckSystem.Judgement import DiffCalculator
from InfoProcessor import Updater
import numpy as np

from skip import skip

CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3


PATH = "../res/skin4/"
WIDTH = 1920
HEIGHT = 1080
FPS = 60
PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8  # actual playfield is smaller than screen res
PLAYFIELD_SCALE = PLAYFIELD_WIDTH / 512
SCALE = HEIGHT / 768
MOVE_RIGHT = int(WIDTH * 0.2)  # center the playfield
MOVE_DOWN = int(HEIGHT * 0.1)


start_time = time.time()


class Object:
	def __init__(self, cursor_x, cursor_y, beatmap, skin, check, pcircle, pslider, pspinner):
		self.cursor = Cursor(PATH + "cursor", SCALE)
		self.cursor_trail = Cursortrail(PATH + "cursortrail", cursor_x, cursor_y, SCALE)
		# self.lifegraph = LifeGraph(PATH + "scorebar-colour")

		self.scoreentry = ScoreEntry(PATH, SCALE, skin.colours["InputOverlayText"])

		self.key1 = InputOverlay(PATH, SCALE, [255, 255, 0], self.scoreentry)
		self.key2 = InputOverlay(PATH, SCALE, [255, 255, 0], self.scoreentry)
		self.mouse1 = InputOverlay(PATH, SCALE, [255, 0, 255], self.scoreentry)
		self.mouse2 = InputOverlay(PATH, SCALE, [255, 0, 255], self.scoreentry)

		self.scorenumbers = ScoreNumbers(PATH, SCALE)
		self.accuracy = Accuracy(self.scorenumbers, WIDTH, HEIGHT, skin.fonts["ScoreOverlap"], SCALE)
		# self.timepie = TimePie(SCALE, self.accuracy)
		# self.hitresult = HitResult(PATH, SCALE, PLAYFIELD_SCALE, self.accuracy)
		# self.spinbonus = SpinBonusScore(SCALE, skin.fonts["ScoreOverlap"], self.scorenumbers, WIDTH, HEIGHT)
		# self.combocounter = ComboCounter(self.scorenumbers, WIDTH, HEIGHT, skin.fonts["ScoreOverlap"], SCALE)
		self.scorecounter = ScoreCounter(self.scorenumbers, beatmap.diff, WIDTH, HEIGHT, skin.fonts["ScoreOverlap"], SCALE)
		#
		# self.urbar = URBar(SCALE, check.scorewindow, WIDTH, HEIGHT)
		#
		# self.followpoints = FollowPointsManager(PATH + "followpoint", PLAYFIELD_SCALE, MOVE_DOWN, MOVE_RIGHT)

		self.circle = CircleManager(pcircle, check.ar())
		self.slider = SliderManager(pslider, beatmap.diff, PLAYFIELD_SCALE, skin, MOVE_DOWN, MOVE_RIGHT)
		self.spinner = SpinnerManager(pspinner, PLAYFIELD_SCALE, MOVE_RIGHT, MOVE_DOWN)
		self.hitobjmanager = HitObjectManager(self.circle, self.slider, self.spinner, check.scorewindow[2])


def nearer(cur_time, replay, index):
	# decide the next replay_data index, by finding the closest to the cur_time
	min_time = abs(replay[index][TIMES] - cur_time)
	min_time_toskip = min(min_time, abs(replay[index+1][TIMES] - cur_time))

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


def find_followp_target(beatmap, index=0):
	# reminder: index means the previous circle. the followpoints will point to the circle of index+1

	while "spinner" in beatmap.hitobjects[index + 1]["type"] or "new combo" in beatmap.hitobjects[index + 1]["type"]:
		index += 1

	if "end" in beatmap.hitobjects[index + 1]["type"]:
		return index * 10, beatmap.hitobjects[index]["end time"] * 10, 0, 0

	osu_d = beatmap.hitobjects[index]
	x_end = osu_d["end x"]
	y_end = osu_d["end y"]

	object_endtime = osu_d["end time"]

	return index, object_endtime, x_end, y_end


def setupBackground():
	img = Image.new("RGB", (WIDTH, HEIGHT))  # setup background
	# playfield = Playfield(PATH + "scorebar-bg", WIDTH, HEIGHT)
	# playfield.add_to_frame(img)
	inputoverlayBG = InputOverlayBG(PATH + "inputoverlay-background", SCALE)
	inputoverlayBG.add_to_frame(img, WIDTH - int(inputoverlayBG.orig_cols / 2), int(320 * SCALE))
	return img


def keys(n):
	k1 = n & 5 == 5
	k2 = n & 10 == 10
	m1 = not k1 and n & 1 == 1
	m2 = not k2 and n & 2 == 2
	smoke = n & 16 == 16
	return k1, k2, m1, m2  # fuck smoke


def create_frame(filename, beatmap, skin, replay_event, resultinfo, start_index, end_index):
	writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*"X264"), FPS, (WIDTH, HEIGHT))
	print("process start")
	orig_img = setupBackground()

	old_cursor_x = int(replay_event[0][CURSOR_X] * PLAYFIELD_SCALE) + MOVE_RIGHT
	old_cursor_y = int(replay_event[0][CURSOR_Y] * PLAYFIELD_SCALE) + MOVE_RIGHT

	diffcalculator = DiffCalculator(beatmap.diff)
	time_preempt = diffcalculator.ar()

	prepare_timer = time.time()

	pcircle = PrepareCircles(beatmap, PATH, PLAYFIELD_SCALE, skin)
	pcircle = pcircle.get_frames()

	pslider = PrepareSlider(PATH, beatmap.diff, PLAYFIELD_SCALE, skin, MOVE_DOWN, MOVE_RIGHT)
	pslider = pslider.get_frames()

	pspinner = PrepareSpinner(PLAYFIELD_SCALE, PATH)
	pspinner = pspinner.get_frames()

	component = Object(old_cursor_x, old_cursor_y, beatmap, skin, diffcalculator, pcircle, pslider, pspinner)
	prepare_timer = time.time() - prepare_timer

	preempt_followpoint = 800

	updater = Updater(resultinfo, component, PLAYFIELD_SCALE, MOVE_DOWN, MOVE_RIGHT)

	simulate = replay_event[start_index][TIMES]
	cur_time, index_hitobject, info_index, osr_index, index_followpoint, object_endtime, x_end, y_end = skip(simulate, resultinfo, replay_event, beatmap.hitobjects, time_preempt, component)
	cursor_event = replay_event[osr_index]
	updater.info_index = info_index
	img = Image.new("RGB", (1,1))
	print("setup done")
	timer = 0
	timer2 = 0
	while osr_index < end_index: # len(replay_event) - 3:
		if osr_index >= start_index:
			img = orig_img.copy()  # reset background

		k1, k2, m1, m2 = keys(cursor_event[KEYS_PRESSED])
		if k1:
			component.key1.clicked(cursor_event[TIMES])
		if k2:
			component.key2.clicked(cursor_event[TIMES])
		if m1:
			component.mouse1.clicked(cursor_event[TIMES])
		if m2:
			component.mouse2.clicked(cursor_event[TIMES])

		osu_d = beatmap.hitobjects[index_hitobject]
		x_circle = int(osu_d["x"] * PLAYFIELD_SCALE) + MOVE_RIGHT
		y_circle = int(osu_d["y"] * PLAYFIELD_SCALE) + MOVE_DOWN


		# check if it's time to draw followpoints
		if cur_time + preempt_followpoint >= object_endtime and index_followpoint + 2 < len(beatmap.hitobjects):
			index_followpoint += 1
			#component.followpoints.add_fp(x_end, y_end, object_endtime, beatmap.hitobjects[index_followpoint])
			index_followpoint, object_endtime, x_end, y_end = find_followp_target(beatmap, index_followpoint)


		# check if it's time to draw circles
		if cur_time + time_preempt >= osu_d["time"] and index_hitobject + 1 < len(beatmap.hitobjects):
			if "spinner" in osu_d["type"]:
				if cur_time + 400 > osu_d["time"]:
					component.hitobjmanager.add_spinner(osu_d["time"], osu_d["end time"], cur_time)
					index_hitobject += 1
			else:

				component.hitobjmanager.add_circle(x_circle, y_circle, cur_time, osu_d)

				if "slider" in osu_d["type"]:
					component.hitobjmanager.add_slider(osu_d, x_circle, y_circle, cur_time)
				index_hitobject += 1

		updater.update(cur_time)

		asdf = time.time()
		component.key1.add_to_frame(img, WIDTH - int(24 * SCALE), int(350 * SCALE))
		component.key2.add_to_frame(img, WIDTH - int(24 * SCALE), int(398 * SCALE))
		component.mouse1.add_to_frame(img, WIDTH - int(24 * SCALE), int(446 * SCALE))
		component.mouse2.add_to_frame(img, WIDTH - int(24 * SCALE), int(494 * SCALE))
		# component.followpoints.add_to_frame(img, cur_time)
		component.hitobjmanager.add_to_frame(img)
		timer2 += time.time() - asdf
		# component.hitresult.add_to_frame(img)
		# component.spinbonus.add_to_frame(img)
		# component.combocounter.add_to_frame(img)
		# component.scorecounter.add_to_frame(img, cursor_event[TIMES])
		# component.accuracy.add_to_frame(img)
		# component.timepie.add_to_frame(img, cur_time, beatmap.end_time)
		# component.urbar.add_to_frame(img)

		cursor_x = int(cursor_event[CURSOR_X] * PLAYFIELD_SCALE) + MOVE_RIGHT
		cursor_y = int(cursor_event[CURSOR_Y] * PLAYFIELD_SCALE) + MOVE_DOWN
		component.cursor_trail.add_to_frame(img, old_cursor_x, old_cursor_y)
		component.cursor.add_to_frame(img, cursor_x, cursor_y)

		a = time.time()
		im = np.asarray(img)
		im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
		writer.write(im)
		timer += time.time() - a

		old_cursor_x = cursor_x
		old_cursor_y = cursor_y

		cur_time += 1000 / FPS

		# choose correct osr index for the current time because in osr file there might be some lag
		osr_index += nearer(cur_time, replay_event, osr_index)
		# if next_index == 0:
		# 	# trying to smooth out cursor
		# 	cursor_event[CURSOR_X] += (replay_event[osr_index+possible_nextindex][CURSOR_X] - cursor_event[CURSOR_X])//2
		# 	cursor_event[CURSOR_Y] += (replay_event[osr_index+possible_nextindex][CURSOR_Y] - cursor_event[CURSOR_Y])//2
		# else:
		cursor_event = replay_event[osr_index]
	print("process done", filename)
	print(timer)
	print(timer2)
	print(prepare_timer)
	print(Timer.add_to_frame_timer, Timer.newalpha_timer)
	writer.release()
