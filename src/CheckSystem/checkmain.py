import time
from CheckSystem.HitObjectChecker import HitObjectChecker
from Parser import osrparser
from Parser.osrparser import setupReplay
from Parser.osuparser import read_file

CURSOR_X = 0
CURSOR_Y = 1
KEYS_PRESSED = 2
TIMES = 3


def nearer(cur_time, replay, index):
	# decide the next replay_data index, by finding the closest to the cur_time
	min_time = abs(replay[index][TIMES] - cur_time)
	min_time_toskip = min(min_time, abs(replay[index+1][TIMES] - cur_time))

	returnindex = 0
	key_state = replay[index][KEYS_PRESSED]
	for x in range(1, 4):
		delta_t = abs(replay[index + x][TIMES] - cur_time)
		if key_state != replay[index + x][KEYS_PRESSED]:
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


def checkmain(beatmap, replay_event, cur_time):
	osr_index = 0
	index_hitobject = 0
	hitobjectchecker = HitObjectChecker(beatmap)
	FPS = 60
	start_time = time.time()

	while osr_index < len(replay_event) - 3:
		if time.time() - start_time > 60:
			print(time.time() - start_time, str(osr_index) + "/" + str(len(replay_event)), cur_time, index_hitobject)
			start_time = time.time()


		next_index = nearer(cur_time + 1000 / FPS, replay_event, osr_index)

		k1, k2, m1, m2 = keys(replay_event[osr_index][KEYS_PRESSED])
		f_k1, f_k2, f_m1, f_m2 = keys(replay_event[osr_index + 1][KEYS_PRESSED])

		new_k1, new_k2 = f_k1 and not k1, f_k2 and not k2
		new_m1, new_m2 = f_m1 and not m1, f_m2 and not m2
		new_click = [new_k1, new_k2, new_m1, new_m2]

		hitobjectchecker.checkcursor(replay_event, new_click, osr_index+1)
		cur_time += 1000 / FPS

		osr_index += 1
	print("check done")
	return hitobjectchecker.info
