import time
import os
from Judgement import Check
from Objects.Button import InputOverlay, InputOverlayBG, ScoreEntry
from Objects.Components import *
from Objects.Followpoints import FollowPointsManager
from Objects.HitObjects import HitObjectManager
from Objects.Scores import HitResult, SpinBonusScore, ScoreNumbers, ComboCounter, ScoreCounter, Accuracy, URBar
from Parser.osuparser import *
from Parser.osrparser import *
from Parser.skinparser import Skin
import numpy as np

# index for replay_event
CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3

# const
PATH = "../res/skin4/"
WIDTH = 1920
HEIGHT = 1080
FPS = 60
PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8  # actual playfield is smaller than screen res
PLAYFIELD_SCALE = PLAYFIELD_WIDTH / 512
SCALE = HEIGHT / 768
MOVE_RIGHT = int(WIDTH * 0.2)  # center the playfield
MOVE_DOWN = int(HEIGHT * 0.1)
BEATMAP_FILE = "../res/tengaku.osu"
REPLAY_FILE = "../res/ten.osr"
INPUTOVERLAY_STEP = 23
start_time = time.time()


class Object:
	def __init__(self, cursor_x, cursor_y, beatmap, skin, check):
		self.cursor = Cursor(PATH + "cursor.png", SCALE)
		self.cursor_trail = Cursortrail(PATH + "cursortrail.png", cursor_x, cursor_y, SCALE)
		self.lifegraph = LifeGraph(PATH + "scorebar-colour.png")

		self.scoreentry = ScoreEntry(PATH, SCALE, skin.colours["InputOverlayText"])

		self.key1 = InputOverlay(PATH, SCALE, [255, 255, 0], self.scoreentry)
		self.key2 = InputOverlay(PATH, SCALE, [255, 255, 0], self.scoreentry)
		self.mouse1 = InputOverlay(PATH, SCALE, [255, 0, 255], self.scoreentry)
		self.mouse2 = InputOverlay(PATH, SCALE, [255, 0, 255], self.scoreentry)

		self.scorenumbers = ScoreNumbers(PATH, SCALE)
		self.accuracy = Accuracy(self.scorenumbers, WIDTH, HEIGHT, skin.fonts["ScoreOverlap"], SCALE)
		self.timepie = TimePie(SCALE, self.accuracy)
		self.hitresult = HitResult(PATH, SCALE, PLAYFIELD_SCALE, self.accuracy)
		self.spinbonus = SpinBonusScore(SCALE, skin.fonts["ScoreOverlap"], self.scorenumbers)
		self.combocounter = ComboCounter(self.scorenumbers, WIDTH, HEIGHT, skin.fonts["ScoreOverlap"], SCALE)
		self.scorecounter = ScoreCounter(self.scorenumbers, beatmap.diff, WIDTH, HEIGHT, skin.fonts["ScoreOverlap"], SCALE)

		self.urbar = URBar(SCALE, check.diff.scorewindow, WIDTH, HEIGHT)

		self.followpoints = FollowPointsManager(PATH + "followpoint", PLAYFIELD_SCALE, MOVE_DOWN, MOVE_RIGHT)
		self.hitobjectmanager = HitObjectManager(beatmap, PATH, PLAYFIELD_SCALE, skin,
		                                         MOVE_DOWN, MOVE_RIGHT, check, self.urbar,
		                                         self.hitresult, self.spinbonus, self.combocounter, self.scorecounter)


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


def setupBackground():
	img = np.zeros((HEIGHT, WIDTH, 3)).astype('uint8')  # setup background
	playfield = Playfield(PATH + "scorebar-bg.png", WIDTH, HEIGHT)
	playfield.add_to_frame(img)
	inputoverlayBG = InputOverlayBG(PATH + "inputoverlay-background.png", SCALE)
	inputoverlayBG.add_to_frame(img, WIDTH - int(inputoverlayBG.orig_cols / 2), int(320 * SCALE))
	return img


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


def keys(n):
	k1 = n & 5 == 5
	k2 = n & 10 == 10
	m1 = not k1 and n & 1 == 1
	m2 = not k2 and n & 2 == 2
	smoke = n & 16 == 16
	return k1, k2, m1, m2  # fuck smoke


def main():
	writer = cv2.VideoWriter("output.mkv", cv2.VideoWriter_fourcc(*"X264"), FPS, (WIDTH, HEIGHT))

	orig_img = setupBackground()

	skin = Skin(PATH)

	beatmap = read_file(BEATMAP_FILE, PLAYFIELD_SCALE, skin.colours)

	replay_event, cur_time = setupReplay(REPLAY_FILE, beatmap.start_time, beatmap.end_time)
	osr_index = 0

	old_cursor_x = int(replay_event[0][CURSOR_X] * PLAYFIELD_SCALE) + MOVE_RIGHT
	old_cursor_y = int(replay_event[0][CURSOR_Y] * PLAYFIELD_SCALE) + MOVE_RIGHT

	check = Check(beatmap.diff, beatmap.hitobjects)

	component = Object(old_cursor_x, old_cursor_y, beatmap, skin, check)

	index_hitobject = 0
	preempt_followpoint = 800
	index_followpoint, object_endtime, x_end, y_end = find_followp_target(beatmap)

	endtime_fp = beatmap.hitobjects[-1]["time"] + preempt_followpoint * 10
	beatmap.hitobjects.append(
		{"x": 0, "y": 0, "time": endtime_fp, "combo_number": 0, "type": ["end"]})  # to avoid index out of range

	for x in range(10):
		replay_event.append([replay_event[-1][CURSOR_X], replay_event[-1][CURSOR_Y], 0, int(replay_event[-1][TIMES]+1000/FPS)])

	replay_event.append([0, 0, 0, replay_event[-1][3] * 5])
	replay_event.append([0, 0, 0, replay_event[-1][3] * 5])
	cursor_event = replay_event[osr_index]

	start_time = time.time()

	timer = [0, 0, 0, 0]
	print("setup done")

	while osr_index < 5000: #osr_index < len(replay_event) - 3:
		img = np.copy(orig_img)  # reset background

		if time.time() - start_time > 60:
			print(time.time() - start_time, str(osr_index) + "/" + str(len(replay_event)), cur_time, index_hitobject, index_followpoint)
			start_time = time.time()

		k1, k2, m1, m2 = keys(cursor_event[KEYS_PRESSED])
		if k1:
			component.key1.clicked()
		if k2:
			component.key2.clicked()
		if m1:
			component.mouse1.clicked()
		if m2:
			component.mouse2.clicked()

		a = time.time()

		component.key1.add_to_frame(img, WIDTH - int(24 * SCALE), int(350 * SCALE))
		component.key2.add_to_frame(img, WIDTH - int(24 * SCALE), int(398 * SCALE))
		component.mouse1.add_to_frame(img, WIDTH - int(24 * SCALE), int(446 * SCALE))
		component.mouse2.add_to_frame(img, WIDTH - int(24 * SCALE), int(494 * SCALE))

		timer[1] += time.time() - a

		osu_d = beatmap.hitobjects[index_hitobject]
		x_circle = int(osu_d["x"] * PLAYFIELD_SCALE) + MOVE_RIGHT
		y_circle = int(osu_d["y"] * PLAYFIELD_SCALE) + MOVE_DOWN


		# check if it's time to draw followpoints
		if cur_time + preempt_followpoint >= object_endtime and index_followpoint + 2 < len(beatmap.hitobjects):
			index_followpoint += 1
			component.followpoints.add_fp(x_end, y_end, object_endtime, beatmap.hitobjects[index_followpoint])
			index_followpoint, object_endtime, x_end, y_end = find_followp_target(beatmap, index_followpoint)


		# check if it's time to draw circles
		a = time.time()
		if cur_time + component.hitobjectmanager.time_preempt >= osu_d["time"] and index_hitobject + 1 < len(
				beatmap.hitobjects):
			if "spinner" in osu_d["type"]:
				if cur_time + 400 > osu_d["time"]:
					component.hitobjectmanager.add_spinner(osu_d["time"], osu_d["end time"], cur_time, index_hitobject)
					index_hitobject += 1
			else:

				component.hitobjectmanager.add_circle(x_circle, y_circle,
				                                      osu_d["combo_color"],
				                                      osu_d["combo_number"],
				                                      osu_d["time"] - cur_time, osu_d["time"],
				                                      index_hitobject, "slider" in osu_d["type"])

				if "slider" in osu_d["type"]:
					component.hitobjectmanager.add_slider(osu_d, x_circle, y_circle, cur_time, osu_d["time"],
					                                      index_hitobject)
				index_hitobject += 1

		timer[0] += time.time() - a

		a = time.time()
		component.followpoints.add_to_frame(img,cur_time)
		component.hitobjectmanager.add_to_frame(img, osr_index)
		component.hitresult.add_to_frame(img)
		component.spinbonus.add_to_frame(img)
		component.combocounter.add_to_frame(img)
		component.scorecounter.add_to_frame(img)
		component.accuracy.add_to_frame(img)
		component.timepie.add_to_frame(img, cur_time, beatmap.end_time)
		component.urbar.add_to_frame(img)

		cursor_x = int(cursor_event[CURSOR_X] * PLAYFIELD_SCALE) + MOVE_RIGHT
		cursor_y = int(cursor_event[CURSOR_Y] * PLAYFIELD_SCALE) + MOVE_DOWN
		component.cursor_trail.add_to_frame(img, old_cursor_x, old_cursor_y)
		component.cursor.add_to_frame(img, cursor_x, cursor_y)
		timer[1] += time.time() - a

		old_cursor_x = cursor_x
		old_cursor_y = cursor_y

		next_index = nearer(cur_time + 1000 / 60, replay_event, osr_index)
		f_k1, f_k2, f_m1, f_m2 = keys(replay_event[osr_index + next_index][KEYS_PRESSED])
		new_k1, new_k2 = f_k1 and not k1, f_k2 and not k2
		new_m1, new_m2 = f_m1 and not m1, f_m2 and not m2
		new_click = new_k1 + new_k2 + new_m1 + new_m2
		component.hitobjectmanager.checkcursor(replay_event, new_click, osr_index + next_index, img)

		a = time.time() - a
		writer.write(img)
		timer[2] += time.time() - a

		cur_time += 1000 / FPS

		# choose correct osr index for the current time because in osr file there might be some lag
		osr_index += next_index
		# if next_index == 0:
		# 	# trying to smooth out cursor
		# 	cursor_event[CURSOR_X] += (replay_event[osr_index+possible_nextindex][CURSOR_X] - cursor_event[CURSOR_X])//2
		# 	cursor_event[CURSOR_Y] += (replay_event[osr_index+possible_nextindex][CURSOR_Y] - cursor_event[CURSOR_Y])//2
		# else:
		cursor_event = replay_event[osr_index]

	print(beatmap.hitobjects[index_hitobject]["time"])
	print(component.hitresult.total)
	print(timer)
	writer.release()


if __name__ == "__main__":
	main()
	print("Done Converting..")
	os.system("ffmpeg -i output.mkv -c copy output.mp4 -y")
	os.system("rm output.mkv")
# replay_info = osrparse.parse_replay_file("../res/imaginedragons.osr")
# replay_event = setupReplay(replay_info)
# print(replay_event)
