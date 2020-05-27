from ..EEnum.EReplay import Replays


def smoothcursor(replay, osrindex, cursor_event):

	oldx = cursor_event.event[Replays.CURSOR_X]
	oldy = cursor_event.event[Replays.CURSOR_Y]
	newx = 0.6 * oldx + 0.4 * replay[osrindex+1][Replays.CURSOR_X]
	newy = 0.6 * oldy + 0.4 * replay[osrindex+1][Replays.CURSOR_Y]

	keys = cursor_event.event[Replays.KEYS_PRESSED]
	newtime = cursor_event.event[Replays.TIMES] * 0.6 + replay[osrindex+1][Replays.TIMES] * 0.4
	newcursorevent = [None, None, None, None]
	newcursorevent[Replays.CURSOR_X] = newx
	newcursorevent[Replays.CURSOR_Y] = newy
	newcursorevent[Replays.TIMES] = newtime
	newcursorevent[Replays.KEYS_PRESSED] = keys
	return newcursorevent
