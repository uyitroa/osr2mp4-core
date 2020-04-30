import os

from CheckSystem.checkmain import checkmain
from Parser.osrparser import setupReplay
from create_frames import create_frame
from Parser.osuparser import *
from Parser.skinparser import Skin
import json

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


def main():

	data = json.load(open("config.json"))
	skin_path = data["Skin path"]
	beatmap_file = data[".osu path"]
	replay_file = data[".osr path"]
	multi_process = bool(data["Multiprocessing"])
	codec = data["Video codec"]
	output_path = data["Output path"]

	skin = Skin(skin_path)
	beatmap = read_file(beatmap_file, PLAYFIELD_SCALE, skin.colours)
	replay_event, cur_time = setupReplay(replay_file, beatmap.start_time, beatmap.end_time)

	endtime_fp = beatmap.hitobjects[-1]["time"] + 800
	beatmap.hitobjects.append(
		{"x": 0, "y": 0, "time": endtime_fp, "combo_number": 0, "type": ["end"]})  # to avoid index out of range

	resultinfo = checkmain(beatmap, replay_event, cur_time)

	print(resultinfo[-1].accuracy)
	create_frame(output_path, codec, beatmap, skin, skin_path, replay_event, resultinfo, 0, len(replay_event) - 3, multi_process)
	#os.system("ffmpeg -i output.mkv -codec copy output.mp4 -y")


if __name__ == "__main__":
	main()
