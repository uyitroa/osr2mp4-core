from osr2mp4 import logger
from osr2mp4.osrparse.enums import Mod

from osr2mp4.CheckSystem.HitObjectChecker import HitObjectChecker
from osr2mp4.EEnum.EReplay import Replays


def nearer(cur_time, replay, index):
	# decide the next replay_data index, by finding the closest to the cur_time
	min_time = abs(replay[index][Replays.TIMES] - cur_time)
	min_time_toskip = min(min_time, abs(replay[index+1][Replays.TIMES] - cur_time))

	returnindex = 0
	key_state = replay[index][Replays.KEYS_PRESSED]
	for x in range(1, 4):
		delta_t = abs(replay[index + x][Replays.TIMES] - cur_time)
		if key_state != replay[index + x][Replays.KEYS_PRESSED]:
			if delta_t <= min_time_toskip:
				return x
		if delta_t < min_time:
			min_time = delta_t
			returnindex = x

	return returnindex


def keys(n):
	k1 = n & 5 == 5
	k2 = n & 10 == 10
	m1 = not k1 and n & 1 == 1
	m2 = not k2 and n & 2 == 2
	smoke = n & 16 == 16
	return k1, k2, m1, m2  # fuck smoke


def diffmod(replay_info, diff):
	mods = replay_info.mod_combination
	if Mod.HardRock in mods or Mod.HardSoft in mods:
		diff["ApproachRate"] = min(diff["ApproachRate"] * 1.4, 10)
		diff["CircleSize"] = min(diff["CircleSize"] * 1.3, 10)
		diff["HPDrainRate"] = min(diff["HPDrainRate"] * 1.4, 10)
		diff["OverallDifficulty"] = min(diff["OverallDifficulty"] * 1.4, 10)
	if Mod.Easy in mods:
		diff["ApproachRate"] = diff["ApproachRate"] * 0.5
		diff["CircleSize"] = diff["CircleSize"] * 0.5
		diff["HPDrainRate"] = diff["HPDrainRate"] * 0.5
		diff["OverallDifficulty"] = diff["OverallDifficulty"] * 0.5


def checkmain(beatmap, replay_info, settings, tests=False):
	osr_index = 0
	replay_event = replay_info.play_data

	diffmod(replay_info, beatmap.diff)

	hitobjectchecker = HitObjectChecker(beatmap, settings, replay_info, tests)

	break_index = 0
	breakperiod = beatmap.breakperiods[break_index]
	in_break = int(replay_event[osr_index][Replays.TIMES]) in range(breakperiod["Start"], breakperiod["End"])

	logger.debug("Start check")

	while osr_index < len(replay_event) - 3:
		k1, k2, m1, m2 = keys(replay_event[osr_index][Replays.KEYS_PRESSED])
		if not in_break:
			f_k1, f_k2, f_m1, f_m2 = keys(replay_event[osr_index + 1][Replays.KEYS_PRESSED])
		else:
			f_k1, f_k2, f_m1, f_m2 = False, False, False, False

		new_k1, new_k2 = f_k1 and not k1, f_k2 and not k2
		new_m1, new_m2 = f_m1 and not m1, f_m2 and not m2
		new_click = [new_k1, new_k2, new_m1, new_m2]

		hitobjectchecker.checkcursor(replay_event, new_click, osr_index+1, in_break, breakperiod)

		osr_index += 1

		breakperiod = beatmap.breakperiods[break_index]
		next_break = replay_event[osr_index][Replays.TIMES] > breakperiod["End"]

		if next_break:
			break_index = min(break_index + 1, len(beatmap.breakperiods) - 1)
			breakperiod = beatmap.breakperiods[break_index]
			
		in_break = int(replay_event[osr_index][Replays.TIMES]) in range(breakperiod["Start"], breakperiod["End"])

	logger.debug("check done")
	logger.log(1, "RETURN %r", hitobjectchecker.info[-1])
	return hitobjectchecker.info
