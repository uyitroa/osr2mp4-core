import math
from osr2mp4.EEnum.EReplay import Replays
from osr2mp4.osrparse.replay import Replay


def add(replay, x, y, key, rtime):
	r = [None, None, None, None]
	r[Replays.CURSOR_X] = x
	r[Replays.CURSOR_Y] = y
	r[Replays.KEYS_PRESSED] = key
	r[Replays.TIMES] = rtime
	replay.append(r)


def get_auto(beatmap):
	replay = Replay()

	replay_event = []
	timeframe = 1000/60

	width, height = 512, 384

	cur_key = 10
	minbpm = 150
	mintime_stream = 1000/(minbpm * 4/60)

	add(replay_event, width//2, height//2, 0, beatmap.hitobjects[0]["time"] - 5000)

	for i in range(len(beatmap.hitobjects)):
		cur_obj = beatmap.hitobjects[i]

		if i > 0 and cur_obj["time"] - beatmap.hitobjects[i-1]["end time"] < mintime_stream:
			cur_key = 5 if cur_key == 10 else 10
		else:
			cur_key = 10

		if "circle" in cur_obj["type"]:
			add(replay_event, cur_obj["x"], cur_obj["y"], 0, cur_obj["time"]-2)
			add(replay_event, cur_obj["x"], cur_obj["y"], cur_key, cur_obj["time"])
			add(replay_event, cur_obj["x"], cur_obj["y"], 0, cur_obj["time"]+2)

		elif "slider" in cur_obj["type"]:
			add(replay_event, cur_obj["x"], cur_obj["y"], 0, cur_obj["time"] - 2)
			add(replay_event, cur_obj["x"], cur_obj["y"], cur_key, cur_obj["time"])

			for repeat in range(cur_obj["repeated"]):
				for curtime in range(0, int(cur_obj["duration"]), int(timeframe)):
					slidertime = curtime if repeat % 2 == 0 else cur_obj["duration"] - curtime
					t = slidertime/cur_obj["duration"]
					distance = t * cur_obj["pixel length"]

					pos = cur_obj["slider_c"].at(distance)

					add(replay_event, pos[0], pos[1], cur_key, cur_obj["time"] + cur_obj["duration"] * repeat + curtime)
			add(replay_event, cur_obj["end x"], cur_obj["end y"], cur_key, cur_obj["end time"])
			add(replay_event, cur_obj["end x"], cur_obj["end y"], 0, cur_obj["end time"]+2)

		elif "spinner" in cur_obj["type"]:
			speed = 0.85
			rot = 0
			pos_x = width//2
			pos_y = height//2

			radius = 50

			for curtime in range(cur_obj["time"], int(cur_obj["end time"]), int(timeframe)):
				pos_x = math.cos(rot) * radius + width//2
				pos_y = math.sin(rot) * radius + height//2

				add(replay_event, pos_x, pos_y, cur_key, curtime)

				rot += speed
			add(replay_event, pos_x, pos_y, 0, cur_obj["end time"]+2)

	replay_event.sort(key=lambda x: x[Replays.TIMES])  # sort replay data based on time

	replay.play_data = replay_event

	return replay

