import osrparse


# index for replay_event
CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3


def setupReplay(osrfile, start_time, end_time):
	replay_info = osrparse.parse_replay_file(osrfile)
	replay_data = [None] * len(replay_info.play_data)

	total_time = 0
	start_index = 0

	start_osr = max(0, start_time - 3000)

	for index in range(len(replay_data)):
		times = replay_info.play_data[index].time_since_previous_action
		total_time += times

		# if total_time >= end_osr:
		# 	break
		# end_index += 1

		if total_time < start_osr:
			start_index = index + 1  # to crop later, everything before we can ignore
			continue

		replay_data[index] = [None, None, None, None]
		replay_data[index][CURSOR_X] = replay_info.play_data[index].x
		replay_data[index][CURSOR_Y] = replay_info.play_data[index].y
		replay_data[index][KEYS_PRESSED] = replay_info.play_data[index].keys_pressed
		replay_data[index][TIMES] = total_time

	replay_data = replay_data[start_index:-1]
	replay_data.sort(key=lambda x: x[TIMES])  # sort replay data based on time
	start_time = replay_data[0][TIMES]

	for x in range(10):
		replay_data.append([replay_data[-1][CURSOR_X], replay_data[-1][CURSOR_Y], 0, int(replay_data[-1][TIMES]+17)])

	replay_data.append([0, 0, 0, replay_data[-1][3] * 5])
	replay_data.append([0, 0, 0, replay_data[-1][3] * 5])

	return replay_data, start_time
