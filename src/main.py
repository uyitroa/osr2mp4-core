import multiprocessing
from multiprocessing import Process
import os
from create_frames import create_frame
from CheckSystem.checkmain import checkmain
from Parser.osuparser import *
from Parser.osrparser import *
from Parser.skinparser import Skin

# const
PATH = "../res/skin8/"
FPS = 60
WIDTH = 1920
HEIGHT = 1080
PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8  # actual playfield is smaller than screen res
PLAYFIELD_SCALE = PLAYFIELD_WIDTH / 512
SCALE = HEIGHT / 768
MOVE_RIGHT = int(WIDTH * 0.2)  # center the playfield
MOVE_DOWN = int(HEIGHT * 0.1)
BEATMAP_FILE = "../res/tengaku.osu"
REPLAY_FILE = "../res/ten.osr"


def smart_divide(beatmap, n_process, max_osr, replay):
	has_spinner = [0] * n_process
	divided = [[] for _ in range(n_process)]
	filenames = []
	osr_index = 0
	for index in beatmap.spinner_index:
		has_spinner[0] = 1
		found_startindex = False
		while replay[osr_index][3] < beatmap.hitobjects[index]["end time"] + 1000:
			spinnertime = beatmap.hitobjects[index]["time"]
			if spinnertime > replay[osr_index][3] > spinnertime - 1000 and not found_startindex:
				divided[0].append(osr_index)
				found_startindex = True
			osr_index += 1
		if found_startindex:
			divided[0].append(osr_index)
			filenames.append(divided[0][-2])
		else:  # if 2 spinners are too close to each other
			divided[0][-1] = osr_index

	divided[0].append(len(replay)+10)
	divided[0].append(len(replay)+10)

	cur_osr = 0
	cur_spinnerosr = 0
	for x in range(has_spinner[0], len(has_spinner)):
		osr_interval = int((max_osr - cur_osr) / (n_process - x))
		end_osr = cur_osr + osr_interval

		divided[x].append(cur_osr)  # start
		while end_osr > divided[0][cur_spinnerosr+1]:
			filenames.append(divided[x][-1])
			if abs(divided[0][cur_spinnerosr] - divided[x][-1]) <= 100:
				divided[0][cur_spinnerosr] = divided[x].pop()
				filenames.pop()
			else:
				divided[x].append(divided[0][cur_spinnerosr])  # end
			divided[x].append(divided[0][cur_spinnerosr+1])  # start
			cur_spinnerosr += 2

		cur_osr = min(end_osr, divided[0][cur_spinnerosr])
		divided[x].append(cur_osr)  # end

	divided[0].pop()
	divided[0].pop()

	filenames.sort()

	return divided, has_spinner, filenames



def divide_core(max_osr, beatmap, skin, replay_event, resultinfo):
	cpu_count = multiprocessing.cpu_count()
	frame_processes = cpu_count
	processes = []

	divided, has_spinner, filenames = smart_divide(beatmap, frame_processes, max_osr, replay_event)
	print(divided, "\n", has_spinner)
	for x in range(frame_processes):
		processes.append(Process(target=create_frame, args=(beatmap, skin, replay_event, resultinfo, divided[x], has_spinner[x])))

	outputlistfile = open("mylist.txt", "w")
	for video_id in filenames:
		filename = "process" + str(video_id) + ".mkv"
		outputlistfile.write("file " + filename + "\n")
	outputlistfile.close()
	return processes


def main():
	skin = Skin(PATH)
	beatmap = read_file(BEATMAP_FILE, PLAYFIELD_SCALE, skin.colours)
	replay_event, cur_time = setupReplay(REPLAY_FILE, beatmap.start_time, beatmap.end_time)

	endtime_fp = beatmap.hitobjects[-1]["time"] + 800
	beatmap.hitobjects.append(
		{"x": 0, "y": 0, "time": endtime_fp, "combo_number": 0, "type": ["end"]})  # to avoid index out of range

	for x in range(10):
		replay_event.append([replay_event[-1][CURSOR_X], replay_event[-1][CURSOR_Y], 0, int(replay_event[-1][TIMES]+1000/FPS)])

	replay_event.append([0, 0, 0, replay_event[-1][3] * 5])
	replay_event.append([0, 0, 0, replay_event[-1][3] * 5])

	resultinfo = checkmain(beatmap, replay_event, cur_time)

	processes = divide_core(len(replay_event) - 3, beatmap, skin, replay_event, resultinfo)

	for x in processes:
		x.start()

	for x in processes:
		x.join()

	print("Done Converting..")
	os.system("ffmpeg -f concat -i mylist.txt -c copy output.mp4 -y")

	# TODO: wrong filename
	for x in range(len(processes)):
		filename = "process" + str(x) + ".mkv"
		os.system("rm " + filename)
	os.system("rm mylist.txt")



if __name__ == "__main__":
	main()

