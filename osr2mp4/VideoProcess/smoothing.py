from osr2mp4.EEnum.EReplay import Replays


def smoothcursor(replay, osrindex, actual_time):
	prev = replay[max(0, osrindex - 1)]
	nexto = replay[osrindex]
	ratio = 1
	if (nexto[Replays.TIMES] - prev[Replays.TIMES]) != 0:
		ratio = (1 - (nexto[Replays.TIMES] - actual_time) / (nexto[Replays.TIMES] - prev[Replays.TIMES]))

	cx = prev[Replays.CURSOR_X] + (nexto[Replays.CURSOR_X] - prev[Replays.CURSOR_X]) * ratio
	cy = prev[Replays.CURSOR_Y] + (nexto[Replays.CURSOR_Y] - prev[Replays.CURSOR_Y]) * ratio
	return cx, cy
