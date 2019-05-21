import time
import os
from Objects.Components import *
from Objects.HitObjects import Circles, Slider
from Parser.osuparser import *
from Parser.osrparser import *
from Parser.skinparser import Skin
import numpy as np
import ray

ray.init()

# index for replay_event
CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3

# const
PATH = "../res/skin2/"
WIDTH = 1920
HEIGHT = 1080
FPS = 60
PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8  # actual playfield is smaller than screen res
SCALE = PLAYFIELD_WIDTH / 512
MOVE_TO_RIGHT = int(WIDTH * 0.2)  # center the playfield
MOVE_DOWN = int(HEIGHT * 0.1)
BEATMAP_FILE = "../res/freedomdive.osu"
REPLAY_FILE = "../res/fd.osr"
start_time = time.time()

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


def nearer(cur_time, replay, index):
	# decide the next replay_data index, by finding the closest to the cur_time
	time0 = abs(replay[index][TIMES] - cur_time)
	time1 = abs(replay[index + 1][TIMES] - cur_time)
	time2 = abs(replay[index + 2][TIMES] - cur_time)
	time3 = abs(replay[index + 3][TIMES] - cur_time)
	values = [time0, time1, time2, time3]
	return min(range(len(values)), key=values.__getitem__)  # get index of the min item


def setupBackground():
	img = np.zeros((HEIGHT, WIDTH, 3)).astype('uint8')  # setup background
	playfield = Playfield(PATH + "scorebar-bg.png", WIDTH, HEIGHT)
	playfield.add_to_frame(img)
	inputoverlayBG = InputOverlayBG(PATH + "inputoverlay-background.png")
	inputoverlayBG.add_to_frame(img, WIDTH - int(inputoverlayBG.orig_cols/2), int(HEIGHT/2))
	return img


def main():

	writer = cv2.VideoWriter("output.mkv", cv2.VideoWriter_fourcc(*"X264"), FPS, (WIDTH, HEIGHT))

	orig_img = setupBackground()

	skin = Skin(PATH)

	beatmap = read_file(BEATMAP_FILE, SCALE, skin.colours)

	replay_event, cur_time = setupReplay(REPLAY_FILE, beatmap.start_time, beatmap.end_time)
	osr_index = 0

	old_cursor_x = int(replay_event[0][CURSOR_X] * SCALE) + MOVE_TO_RIGHT
	old_cursor_y = int(replay_event[0][CURSOR_Y] * SCALE) + MOVE_TO_RIGHT

	component = Object(PATH, old_cursor_x, old_cursor_y, beatmap.diff, beatmap.max_combo, 38,
	                   beatmap.slider_combo, skin.colours)

	index_hitobject = 0
	cur_offset = 0
	beatmap.hitobjects.append({"x": 0, "y": 0, "time": float('inf'), "combo_number": 0})  # to avoid index out of range
	print("setup done")
	while osr_index < 1000:  # len(replay_event) - 3
		if int(cur_time) % int(1000 / FPS * 100) < 10:
			print("\n\nCurrent time:", cur_time)
			print("Running for:", time.time() - start_time)
			print("Osr index:", osr_index)
			print("hit object index:", index_hitobject)
			print("Offset index:", cur_offset)
		img = np.copy(orig_img)  # reset background

		cursor_x = int(replay_event[osr_index][CURSOR_X] * SCALE) + MOVE_TO_RIGHT
		cursor_y = int(replay_event[osr_index][CURSOR_Y] * SCALE) + MOVE_DOWN

		if replay_event[osr_index][KEYS_PRESSED] == 10 or replay_event[osr_index][KEYS_PRESSED] == 15:
			component.key2.clicked()
		if replay_event[osr_index][KEYS_PRESSED] == 5 or replay_event[osr_index][KEYS_PRESSED] == 15:
			component.key1.clicked()
		component.key1.add_to_frame(img, WIDTH - int(component.key1.orig_cols/2), int(HEIGHT/2) - 80)
		component.key2.add_to_frame(img, WIDTH - int(component.key2.orig_cols/2), int(HEIGHT/2) - 30)

		x_circle = int(beatmap.hitobjects[index_hitobject]["x"] * SCALE) + MOVE_TO_RIGHT
		y_circle = int(beatmap.hitobjects[index_hitobject]["y"] * SCALE) + MOVE_DOWN

		if cur_time + component.circles.time_preempt >= beatmap.hitobjects[index_hitobject]["time"]:
			isSlider = 0
			if "slider" in beatmap.hitobjects[index_hitobject]["type"]:
				isSlider = 1
				component.sliders.add_slider(beatmap.hitobjects[index_hitobject]["slider_img"],
				                             beatmap.hitobjects[index_hitobject]["x_offset"],
				                             beatmap.hitobjects[index_hitobject]["y_offset"],
				                             x_circle, y_circle,
				                             beatmap.hitobjects[index_hitobject]["pixel_length"],
				                             beatmap.timing_point[cur_offset]["BeatDuration"])

			component.circles.add_circle(x_circle, y_circle, beatmap.hitobjects[index_hitobject]["combo_color"],
			                             beatmap.hitobjects[index_hitobject]["combo_number"],
			                             isSlider)
			index_hitobject += 1
		component.sliders.add_to_frame(img)
		component.circles.add_to_frame(img)

		component.cursor_trail.add_to_frame(img, old_cursor_x, old_cursor_y)
		component.cursor.add_to_frame(img, cursor_x, cursor_y)
		old_cursor_x = cursor_x
		old_cursor_y = cursor_y
		writer.write(img)

		cur_time += 1000 / FPS
		osr_index += nearer(cur_time, replay_event, osr_index)
		if cur_time + component.circles.time_preempt > beatmap.timing_point[cur_offset + 1]["Offset"]:
			cur_offset += 1
			if cur_time + component.circles.time_preempt > beatmap.timing_point[cur_offset + 1]["Offset"]:
				cur_offset += 1

	writer.release()


if __name__ == "__main__":
	main()
	print("Done Converting..")
	os.system("ffmpeg -i output.mkv -c copy output.mp4 -y")
# replay_info = osrparse.parse_replay_file("../res/imaginedragons.osr")
# replay_event = setupReplay(replay_info)
# print(replay_event)
