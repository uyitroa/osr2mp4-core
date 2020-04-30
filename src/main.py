import os

from CheckSystem.checkmain import checkmain
from Parser.osrparser import setupReplay, TIMES
from create_frames import create_frame
from Parser.osuparser import *
from Parser.skinparser import Skin
import json
import time

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


def findTime(starttime, endtime, replay):
	startindex = None
	endindex = len(replay) - 3
	if endtime == -1:
		endindex = len(replay) - 3
	for index, x in enumerate(replay):
		if x[TIMES] >= starttime * 1000 and startindex is None:
			startindex = index
		if x[TIMES] >= (endtime+1) * 1000 and endtime != -1:
			endindex = index
			break
	return startindex, endindex


def main():

	data = json.load(open("config.json"))
	skin_path = data["Skin path"]
	beatmap_file = data[".osu path"]
	replay_file = data[".osr path"]
	multi_process = bool(data["Multiprocessing"])
	codec = data["Video codec"]
	output_path = data["Output path"]
	start_time = data["Start time"]
	end_time = data["End time"]

	if skin_path[-1] != "/" and skin_path[-1] != "\\":
		skin_path += "/"

	skin = Skin(skin_path)
	beatmap = read_file(beatmap_file, PLAYFIELD_SCALE, skin.colours)
	replay_event, cur_time = setupReplay(replay_file, beatmap.start_time, beatmap.end_time)
	start_index, end_index = findTime(start_time, end_time, replay_event)

	endtime_fp = beatmap.hitobjects[-1]["time"] + 800
	beatmap.hitobjects.append(
		{"x": 0, "y": 0, "time": endtime_fp, "combo_number": 0, "type": ["end"]})  # to avoid index out of range

	resultinfo = checkmain(beatmap, replay_event, cur_time)

	print(resultinfo[-1].accuracy)
	create_frame(output_path, codec, beatmap, skin, skin_path, replay_event, resultinfo, start_index, end_index, multi_process)
	# os.system("ffmpeg -i output.mkv -codec copy output.mp4 -y")


if __name__ == "__main__":
	asdf = time.time()
	main()
	print("\nTotal time:", time.time() - asdf)
