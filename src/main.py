import osrparse
import os
from Components import *
from osuparser import *

# index for replay_event
CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3
LIFE_BAR = 4

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

		self.circles = Circles(path + "hitcircle.png", path, diff, scale, path + "approachcircle.png", maxcombo, gap)


def setupReplay(replay_info):
	replay_data = [None] * len(replay_info.play_data)

	life_bar_graph = replay_info.life_bar_graph.split(",")
	life_bar_graph[-1] = 'inf|1'
	cur_life = life_bar_graph[0].split("|")
	cur_life[0], cur_life[1] = float(cur_life[0]), float(cur_life[1])

	total_time = 0
	start_index = 0
	end_index = 0
	start_time = cur_life[0] - 3000 # gameplay start
	end_time = int(life_bar_graph[-2].split("|")[0]) + 1000 # gameplay end
	for index in range(len(replay_data)):
		times = replay_info.play_data[index].time_since_previous_action
		total_time += times
		if total_time >= end_time:
			break
		end_index += 1
		if total_time < start_time:
			start_index += 1
			continue
		replay_data[index] = [None, None, None, None, None]
		replay_data[index][CURSOR_X] = replay_info.play_data[index].x
		replay_data[index][CURSOR_Y] = replay_info.play_data[index].y
		replay_data[index][KEYS_PRESSED] = replay_info.play_data[index].keys_pressed
		replay_data[index][TIMES] = total_time
	replay_data = replay_data[start_index:end_index]
	replay_data.sort(key=lambda x: x[3]) # sort replay data based on the third elements
	intervals = 1000/60
	life_index = 0
	start_time = replay_data[0][TIMES]
	for index2 in range(len(replay_data) - 1):
		delta = replay_data[index2 + 1][TIMES] - replay_data[index2][TIMES]
		if replay_data[index2][TIMES] > cur_life[0]:
			life_index += 1
			cur_life = life_bar_graph[life_index].split("|")
			cur_life[0], cur_life[1] = float(cur_life[0]), float(cur_life[1])
		replay_data[index2][LIFE_BAR] = cur_life[1]

		# quick maths
		ratio = delta / intervals
		round_ratio = round(ratio)

		replay_data[index2][TIMES] = round_ratio
		replay_data[index2 + 1][TIMES] += ratio - round_ratio
	replay_data[-1][LIFE_BAR] = cur_life[1]
	replay_data[-1][TIMES] = int(intervals)
	replay_data[0][TIMES] = 0
	return replay_data, start_time


def main():
	playfield_width, playfield_height = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8
	scale = playfield_width/512
	move_to_right = int(WIDTH * 0.2)
	move_down = int(HEIGHT * 0.2)
	fps = 60
	writer = cv2.VideoWriter("output.mkv", cv2.VideoWriter_fourcc(*"X264"), fps, (WIDTH, HEIGHT))
	img = np.zeros((HEIGHT, WIDTH, 3)).astype('uint8') # setup background
	playfield = Playfield(PATH + "scorebar-bg.png", WIDTH, HEIGHT)
	playfield.add_to_frame(img)
	orig_img = img.copy()

	replay_info = osrparse.parse_replay_file("../res/future.osr")
	replay_event, start_time = setupReplay(replay_info)

	old_cursor_x = int(replay_event[0][CURSOR_X] * scale) + move_to_right
	old_cursor_y = int(replay_event[0][CURSOR_Y] * scale) + move_to_right

	beatmap = read_file("../res/futurecider.osu")

	skin = Skin(PATH, old_cursor_x, old_cursor_y, beatmap.diff, scale, beatmap.max_combo, 38)

	index_hitobject = 0
	cs = (54.4 - 4.48 * beatmap.diff["CircleSize"]) * scale
	beatmap.hitobjects.append({"x": 0, "y": 0, "time": float('inf'), "combo_number": 0})
	for i in range(len(replay_event)): #len(replay_event)
		for n in range(replay_event[i][TIMES]):
			img = np.copy(orig_img)
			cursor_x = int(replay_event[i][CURSOR_X] * scale) + move_to_right
			cursor_y = int(replay_event[i][CURSOR_Y] * scale) + move_down


			if replay_event[i][KEYS_PRESSED] == 10 or replay_event[i][KEYS_PRESSED] == 15:
				skin.key2.clicked()
			if replay_event[i][KEYS_PRESSED] == 5 or replay_event[i][KEYS_PRESSED] == 15:
				skin.key1.clicked()
			skin.cursor_trail.add_to_frame(img, old_cursor_x, old_cursor_y)
			skin.cursor.add_to_frame(img, cursor_x, cursor_y)
			skin.key1.add_to_frame(img, 1800, 450)
			skin.key2.add_to_frame(img, 1800, 500)
			skin.lifegraph.goes_to(replay_event[i][LIFE_BAR])
			skin.lifegraph.add_to_frame(img)

			x_circle = int(beatmap.hitobjects[index_hitobject]["x"] * scale) + move_to_right
			y_circle = int(beatmap.hitobjects[index_hitobject]["y"] * scale) + move_down
			if start_time + skin.circles.time_preempt >= beatmap.hitobjects[index_hitobject]["time"]:
				skin.circles.add_circle(x_circle, y_circle, beatmap.hitobjects[index_hitobject]["combo_number"])
				index_hitobject += 1
			skin.circles.add_to_frame(img)


			old_cursor_x = cursor_x
			old_cursor_y = cursor_y
			writer.write(img)
			start_time += 1000/60

	writer.release()


if __name__ == "__main__":
	main()
	print("Done Converting..")
	os.system("ffmpeg -i output.mkv -c copy output.mp4 -y")
	# replay_info = osrparse.parse_replay_file("../res/imaginedragons.osr")
	# replay_event = setupReplay(replay_info)
	# print(replay_event)
