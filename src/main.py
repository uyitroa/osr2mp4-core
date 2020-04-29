import multiprocessing
from multiprocessing import Process
import os

from CheckSystem.checkmain import checkmain
from Parser.osrparser import setupReplay, CURSOR_Y, CURSOR_X, TIMES
from create_frames import create_frame
from Parser.osuparser import *
from Parser.skinparser import Skin

# const
WIDTH = 1920
HEIGHT = 1080
FPS = 60
PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8  # actual playfield is smaller than screen res
PLAYFIELD_SCALE = PLAYFIELD_WIDTH / 512
SCALE = HEIGHT / 768
MOVE_RIGHT = int(WIDTH * 0.2)  # center the playfield
MOVE_DOWN = int(HEIGHT * 0.1)
INPUTOVERLAY_STEP = 23


def divide_core(max_osr, beatmap, skin, replay_event, resultinfo):
	cpu_count = multiprocessing.cpu_count()
	frame_processes = cpu_count - 1
	processes = []
	osr_interval = int(max_osr / frame_processes)

	start_index = 0
	outputlistfile = open("mylist.txt", "w")
	for x in range(frame_processes):
		if x == frame_processes-1:
			end_index = max_osr
		else:
			end_index = start_index + osr_interval

		filename = "process" + str(x) + ".mkv"
		processes.append(Process(target=create_frame, args=(filename, beatmap, skin, replay_event, resultinfo, start_index, end_index)))
		start_index += osr_interval

		outputlistfile.write("file " + filename + "\n")
	outputlistfile.close()
	return processes


def main():

	skin_path = "../res/skin4/"
	beatmap_file = "../res/thegame.osu"
	replay_file = "../res/thegame.osr"

	skin = Skin(skin_path)
	beatmap = read_file(beatmap_file, PLAYFIELD_SCALE, skin.colours)
	replay_event, cur_time = setupReplay(replay_file, beatmap.start_time, beatmap.end_time)

	endtime_fp = beatmap.hitobjects[-1]["time"] + 800
	beatmap.hitobjects.append(
		{"x": 0, "y": 0, "time": endtime_fp, "combo_number": 0, "type": ["end"]})  # to avoid index out of range
	# a = open("tengaku.txt", "w")
	# a.write(str(beatmap.hitobjects))
	# a.close()
	for x in range(10):
		replay_event.append([replay_event[-1][CURSOR_X], replay_event[-1][CURSOR_Y], 0, int(replay_event[-1][TIMES]+1000/FPS)])

	replay_event.append([0, 0, 0, replay_event[-1][3] * 5])
	replay_event.append([0, 0, 0, replay_event[-1][3] * 5])

	resultinfo = checkmain(beatmap, replay_event, cur_time)

	create_frame("output.mkv", beatmap, skin, skin_path, replay_event, resultinfo, 0, len(replay_event) - 3)
	os.system("ffmpeg -i output.mkv -codec copy output.mp4 -y")


if __name__ == "__main__":
	main()

