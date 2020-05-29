import osrparse


# index for replay_event
from ..CheckSystem.Judgement import DiffCalculator


# noinspection PyTypeChecker
from ..EEnum.EReplay import Replays


def setupReplay(osrfile, beatmap):
	replay_info = osrparse.parse_replay_file(osrfile)
	replay_data = [None] * len(replay_info.play_data)

	start_time = beatmap.start_time

	total_time = 0
	start_index = 1

	start_osr = start_time - 3000

	for index in range(len(replay_data)):
		times = replay_info.play_data[index].time_since_previous_action
		total_time += times

		# if total_time >= end_osr:
		# 	break
		# end_index += 1

		if total_time < start_osr:
			start_index += + 1  # to crop later, everything before we can ignore
			continue

		replay_data[index] = [None, None, None, None]
		replay_data[index][Replays.CURSOR_X] = replay_info.play_data[index].x
		replay_data[index][Replays.CURSOR_Y] = replay_info.play_data[index].y
		replay_data[index][Replays.KEYS_PRESSED] = replay_info.play_data[index].keys_pressed
		replay_data[index][Replays.TIMES] = total_time

	replay_data = replay_data[start_index:-1]
	replay_data.sort(key=lambda x: x[Replays.TIMES])  # sort replay data based on time

	start_time = replay_data[0][Replays.TIMES]

	for x in range(10):
		replay_data.append([replay_data[-1][Replays.CURSOR_X], replay_data[-1][Replays.CURSOR_Y], 0, max(replay_data[-1][Replays.TIMES], int(beatmap.end_time + 1000) + 17 * x)])

	diffcalculator = DiffCalculator(beatmap.diff)
	timepreempt = diffcalculator.ar()
	if replay_data[0][Replays.TIMES] > beatmap.hitobjects[0]["time"] - timepreempt - 2000:
		startdata = replay_data[0].copy()
		startdata[Replays.TIMES] = beatmap.hitobjects[0]["time"] - timepreempt - 2000
		replay_data.insert(0, startdata)


	replay_data.append([0, 0, 0, replay_data[-1][3] * 5])
	replay_data.append([0, 0, 0, replay_data[-1][3] * 5])

	start_time = replay_data[0][Replays.TIMES]
	beatmap.breakperiods.append({"Start": int(beatmap.end_time + 200), "End": replay_data[-1][Replays.TIMES] + 100, "Arrow": False})

	return replay_data, start_time
