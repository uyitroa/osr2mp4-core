from ..CheckSystem.Judgement import DiffCalculator
from ..EEnum.EReplay import Replays
from ..Utils.skip import search_time, search_osrindex


def get_offset(beatmap, start_index, end_index, replay_event, endtime):
	if endtime == -1:
		endtime = 5000
	else:
		endtime = 0
	start_time = replay_event[start_index][3]
	diffcalculator = DiffCalculator(beatmap.diff)
	timepreempt = diffcalculator.ar()
	hitobjectindex = search_time(start_time, beatmap.hitobjects)
	to_time = min(beatmap.hitobjects[hitobjectindex]["time"] - timepreempt, start_time)
	osr_index = search_osrindex(to_time, replay_event)
	print(replay_event[start_index][3], replay_event[osr_index][3])
	index = max(osr_index, start_index)
	# print(replay_event[osr_index][Replays.TIMES], replay_event[start_index][Replays.TIMES], replay_event[index][Replays.TIMES])
	offset = replay_event[index][3]
	endtime += replay_event[end_index][3] + 100
	print("\n\nOFFSET:", offset)
	return offset, endtime


def find_time(starttime, endtime, replay, settings):

	starttime *= settings.timeframe
	starttime += replay[0][Replays.TIMES]
	starttime = min(starttime, replay[-15][Replays.TIMES])

	if endtime != -1:
		endtime *= settings.timeframe
		# endtime += replay_start
		endtime += replay[0][Replays.TIMES]

		endtime = max(endtime, starttime - 900)

	startindex = None

	if starttime == 0:
		startindex = 0

	endindex = len(replay) - 3
	if endtime == -1:
		endindex = len(replay) - 3

	for index, x in enumerate(replay[:-3]):
		if x[3] >= starttime and startindex is None:
			startindex = index
		if x[3] >= endtime + 1000 and endtime != -1:
			endindex = index
			break
	return startindex, endindex
