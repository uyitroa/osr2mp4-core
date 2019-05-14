import time
from Objects.Components import *
from Objects.HitObjects import Circles, Slider
from Parser.osuparser import *
from Parser.osrparser import *
from Parser.skinparser import Skin
import numpy as np

# const
WIDTH = 1920
HEIGHT = 1080
PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8  # actual playfield is smaller than screen res
SCALE = PLAYFIELD_WIDTH / 512


class Object:
	def __init__(self, path, cursor_x, cursor_y, diff, maxcombo, gap, slider_combo, colors):
		self.cursor = Cursor(path + "cursor.png")
		self.key1 = InputOverlay(path + "inputoverlay-key.png")
		self.key2 = InputOverlay(path + "inputoverlay-key.png")
		self.cursor_trail = Cursortrail(path + "cursortrail.png", cursor_x, cursor_y)
		self.lifegraph = LifeGraph(path + "scorebar-colour.png")

		self.circles = Circles(path + "hitcircle.png", path + "hitcircleoverlay.png", path + "sliderstartcircle.png",
		                       slider_combo, path, diff, SCALE, path + "approachcircle.png", maxcombo, gap, colors)
		self.sliders = Slider(diff["SliderMultiplier"], self.circles.time_preempt, self.circles.opacity_interval, SCALE)


class Frames:
	def __init__(self):
		self.hitobject = 0
		self.CURSOR_X = 0
		self.CURSOR_Y = 1
		self.KEYS_PRESSED = 2
		self.TIMES = 3
		self.FPS = 60
		self.MOVE_TO_RIGHT = int(WIDTH * 0.2)  # center the playfield
		self.MOVE_DOWN = int(HEIGHT * 0.1)
		self.SKIN_PATH = "../res/skin2/"
		self.BEATMAP_FILE = "../res/freedomdive.osu"
		self.REPLAY_FILE = "../res/fd.osr"
		self.start_time = time.time()

		self.orig_img = self.setupBackground()

		self.skin = Skin(self.SKIN_PATH)

		self.beatmap = read_file(self.BEATMAP_FILE, SCALE, self.skin.colours)

		self.replay_event, self.cur_time = setupReplay(self.REPLAY_FILE, self.beatmap.start_time, self.beatmap.end_time)
		self.osr_index = 0

		self.old_cursor_x = int(self.replay_event[0][CURSOR_X] * SCALE) + self.MOVE_TO_RIGHT
		self.old_cursor_y = int(self.replay_event[0][CURSOR_Y] * SCALE) + self.MOVE_TO_RIGHT
		self.cursor_x = self.old_cursor_x
		self.cursor_y = self.old_cursor_y

		self.component = Object(self.SKIN_PATH, self.old_cursor_x, self.old_cursor_y, self.beatmap.diff,
		                        self.beatmap.max_combo, 38,
		                        self.beatmap.slider_combo, self.skin.colours)

		self.cur_offset = 0
		self.beatmap.hitobjects.append(
			{"x": 0, "y": 0, "time": float('inf'), "combo_number": 0})  # to avoid index out of range
		self.img = np.copy(self.orig_img)
		print("setup done")

	def nearer(self, cur_time, replay, index):
		# decide the next replay_data index, by finding the closest to the cur_time
		time0 = abs(replay[index][TIMES] - cur_time)
		time1 = abs(replay[index + 1][TIMES] - cur_time)
		time2 = abs(replay[index + 2][TIMES] - cur_time)
		time3 = abs(replay[index + 3][TIMES] - cur_time)
		values = [time0, time1, time2, time3]
		return min(range(len(values)), key=values.__getitem__)  # get index of the min item

	def setupBackground(self):
		img = np.zeros((HEIGHT, WIDTH, 3)).astype('uint8')  # setup background
		playfield = Playfield(self.SKIN_PATH + "scorebar-bg.png", WIDTH, HEIGHT)
		playfield.add_to_frame(img)
		inputoverlayBG = InputOverlayBG(self.SKIN_PATH + "inputoverlay-background.png")
		inputoverlayBG.add_to_frame(img, WIDTH - int(inputoverlayBG.orig_cols / 2), int(HEIGHT / 2))
		return img

	def edit_frame(self):
		if self.replay_event[self.osr_index][KEYS_PRESSED] == 10 or self.replay_event[self.osr_index][KEYS_PRESSED] == 15:
			self.component.key2.clicked()
		if self.replay_event[self.osr_index][KEYS_PRESSED] == 5 or self.replay_event[self.osr_index][KEYS_PRESSED] == 15:
			self.component.key1.clicked()
		self.component.key1.add_to_frame(self.img, WIDTH - int(self.component.key1.orig_cols / 2), int(HEIGHT / 2) - 80)
		self.component.key2.add_to_frame(self.img, WIDTH - int(self.component.key2.orig_cols / 2), int(HEIGHT / 2) - 30)

		x_circle = int(self.beatmap.hitobjects[self.hitobject]["x"] * SCALE) + self.MOVE_TO_RIGHT
		y_circle = int(self.beatmap.hitobjects[self.hitobject]["y"] * SCALE) + self.MOVE_DOWN

		if self.cur_time + self.component.circles.time_preempt >= self.beatmap.hitobjects[self.hitobject]["time"]:
			isSlider = 0
			if "slider" in self.beatmap.hitobjects[self.hitobject]["type"]:
				isSlider = 1
				self.component.sliders.add_slider(self.beatmap.hitobjects[self.hitobject]["slider_img"],
				                                  self.beatmap.hitobjects[self.hitobject]["x_offset"],
				                                  self.beatmap.hitobjects[self.hitobject]["y_offset"],
				                                  x_circle, y_circle,
				                                  self.beatmap.hitobjects[self.hitobject]["pixel_length"],
				                                  self.beatmap.timing_point[self.cur_offset]["BeatDuration"])

			self.component.circles.add_circle(x_circle, y_circle, self.beatmap.hitobjects[self.hitobject]["combo_color"],
			                                  self.beatmap.hitobjects[self.hitobject]["combo_number"],
			                                  isSlider)
			self.hitobject += 1
		self.component.sliders.add_to_frame(self.img)
		self.component.circles.add_to_frame(self.img)

		self.component.cursor_trail.add_to_frame(self.img, self.old_cursor_x, self.old_cursor_y)
		self.component.cursor.add_to_frame(self.img, self.cursor_x, self.cursor_y)

	def prepare_frame(self, frame_queue):
		queue_index = 0
		while self.osr_index < len(self.replay_event) - 3:  # len(replay_event) - 3
			self.img = np.copy(self.orig_img)  # reset background

			self.cursor_x = int(self.replay_event[self.osr_index][CURSOR_X] * SCALE) + self.MOVE_TO_RIGHT
			self.cursor_y = int(self.replay_event[self.osr_index][CURSOR_Y] * SCALE) + self.MOVE_DOWN

			self.edit_frame()
			frame_queue.put(self.img)
			queue_index += 1
			print(queue_index)

			self.old_cursor_x = self.cursor_x
			self.old_cursor_y = self.cursor_y

			self.cur_time += 1000 / self.FPS
			self.osr_index += self.nearer(self.cur_time, self.replay_event, self.osr_index)
			if self.cur_time + self.component.circles.time_preempt > self.beatmap.timing_point[self.cur_offset + 1]["Offset"]:
				self.cur_offset += 1
				if self.cur_time + self.component.circles.time_preempt > self.beatmap.timing_point[self.cur_offset + 1]["Offset"]:
					self.cur_offset += 1

		print("done preparing frame")
