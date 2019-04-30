import osrparse
import os
from Components import *
from osuparser import *
import numpy as np

# index for replay_event
CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3

# const
PATH = "../res/skin1/"
WIDTH = 1920
HEIGHT = 1080


class Skin:
	def __init__(self, path, cursor_x, cursor_y, diff, scale, maxcombo, gap):
		self.cursor = Cursor(path + "cursor.png")
		self.key1 = InputOverlay(path + "inputoverlay-key.png")
		self.key2 = InputOverlay(path + "inputoverlay-key.png")
		self.cursor_trail = Cursortrail(path + "cursortrail.png", cursor_x, cursor_y)
		self.lifegraph = LifeGraph(path + "scorebar-colour.png")

		self.circles = Circles(path + "hitcircle.png", path + "hitcircleoverlay.png", path, diff, scale, path + "approachcircle.png", maxcombo, gap)


def setupReplay(replay_info, start_time, end_time):
	replay_data = [None] * len(replay_info.play_data)

	total_time = 0
	start_index = 0
	end_index = 0

	start_osr = max(0, start_time - 3000)
	end_osr = end_time + 1000

	for index in range(len(replay_data)):
		times = replay_info.play_data[index].time_since_previous_action
		total_time += times

		if total_time >= end_osr:
			break
		end_index += 1

		if total_time < start_osr:
			start_index = index + 1  # to crop later, everything before we can ignore
			continue

		replay_data[index] = [None, None, None, None]
		replay_data[index][CURSOR_X] = replay_info.play_data[index].x
		replay_data[index][CURSOR_Y] = replay_info.play_data[index].y
		replay_data[index][KEYS_PRESSED] = replay_info.play_data[index].keys_pressed
		replay_data[index][TIMES] = total_time

	replay_data = replay_data[start_index:end_index]
	replay_data.sort(key=lambda x: x[TIMES])  # sort replay data based on time
	start_time = replay_data[0][TIMES]
	return replay_data, start_time


def nearer(cur_time, replay, index):
	time0 = abs(replay[index][TIMES] - cur_time)
	time1 = abs(replay[index + 1][TIMES] - cur_time)
	time2 = abs(replay[index + 2][TIMES] - cur_time)
	time3 = abs(replay[index + 3][TIMES] - cur_time)
	values = [time0, time1, time2, time3]
	return min(range(len(values)), key=values.__getitem__)


def main():
	playfield_width, playfield_height = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8  # actual playfield is smaller than screen res
	scale = playfield_width/512
	move_to_right = int(WIDTH * 0.2)  # center the playfield
	move_down = int(HEIGHT * 0.2)
	fps = 60

	writer = cv2.VideoWriter("output.mkv", cv2.VideoWriter_fourcc(*"X264"), fps, (WIDTH, HEIGHT))
	img = np.zeros((HEIGHT, WIDTH, 3)).astype('uint8') # setup background

	playfield = Playfield(PATH + "scorebar-bg.png", WIDTH, HEIGHT)
	playfield.add_to_frame(img)
	orig_img = img.copy()

	beatmap = read_file("../res/futurecider.osu", scale)

	replay_info = osrparse.parse_replay_file("../res/future.osr")
	replay_event, cur_time = setupReplay(replay_info, beatmap.start_time, beatmap.end_time)
	osr_index = 0

	old_cursor_x = int(replay_event[0][CURSOR_X] * scale) + move_to_right
	old_cursor_y = int(replay_event[0][CURSOR_Y] * scale) + move_to_right

	skin = Skin(PATH, old_cursor_x, old_cursor_y, beatmap.diff, scale, beatmap.max_combo, 38)

	index_hitobject = 0
	beatmap.hitobjects.append({"x": 0, "y": 0, "time": float('inf'), "combo_number": 0})  # to avoid index out of range

	while osr_index < len(replay_event) - 3: #len(replay_event)
		img = np.copy(orig_img)  # reset background

		cursor_x = int(replay_event[osr_index][CURSOR_X] * scale) + move_to_right
		cursor_y = int(replay_event[osr_index][CURSOR_Y] * scale) + move_down

		if replay_event[osr_index][KEYS_PRESSED] == 10 or replay_event[osr_index][KEYS_PRESSED] == 15:
			skin.key2.clicked()
		if replay_event[osr_index][KEYS_PRESSED] == 5 or replay_event[osr_index][KEYS_PRESSED] == 15:
			skin.key1.clicked()
		skin.cursor_trail.add_to_frame(img, old_cursor_x, old_cursor_y)
		skin.cursor.add_to_frame(img, cursor_x, cursor_y)
		skin.key1.add_to_frame(img, 1800, 450)
		skin.key2.add_to_frame(img, 1800, 500)

		x_circle = int(beatmap.hitobjects[index_hitobject]["x"] * scale) + move_to_right
		y_circle = int(beatmap.hitobjects[index_hitobject]["y"] * scale) + move_down
		if cur_time + skin.circles.time_preempt >= beatmap.hitobjects[index_hitobject]["time"]:
			skin.circles.add_circle(x_circle, y_circle, beatmap.hitobjects[index_hitobject]["combo_number"])
			index_hitobject += 1
		skin.circles.add_to_frame(img)


		old_cursor_x = cursor_x
		old_cursor_y = cursor_y
		writer.write(img)

		cur_time += 1000/fps
		osr_index += nearer(cur_time, replay_event, osr_index)

	writer.release()


if __name__ == "__main__":
	main()
	print("Done Converting..")
	os.system("ffmpeg -i output.mkv -c copy output.mp4 -y")
	# replay_info = osrparse.parse_replay_file("../res/imaginedragons.osr")
	# replay_event = setupReplay(replay_info)
	# print(replay_event)
