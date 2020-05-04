import os

import osrparse
from osrparse.enums import Mod
from recordclass import recordclass

from CheckSystem.Judgement import DiffCalculator
from CheckSystem.checkmain import checkmain
from ImageProcess.PrepareFrames.YImage import SkinPaths
from Parser.jsonparser import read
from Parser.osrparser import setupReplay, TIMES
from create_frames import create_frame
from Parser.osuparser import *
from Parser.skinparser import Skin
import time

# const
from skip import search_time, search_osrindex

Settings = recordclass("Settings", "width height fps scale playfieldscale playfieldwidth playfieldheight movedown moveright timeframe")
Paths = recordclass("Paths", "skin defaultskin output ffmpeg")


def findTime(starttime, endtime, replay, replay_start):

	starttime *= 1000
	starttime += replay_start

	if endtime != -1:
		endtime *= 1000
		endtime += replay_start

	startindex = None
	endindex = len(replay) - 3
	if endtime == -1:
		endindex = len(replay) - 3
	for index, x in enumerate(replay):
		if x[TIMES] >= starttime and startindex is None:
			startindex = index
		if x[TIMES] >= endtime + 1000 and endtime != -1:
			endindex = index
			break

	return startindex, endindex


def get_screensize(width, height):
	playfield_width, playfield_height = width * 0.8 * 3 / 4, height * 0.8  # actual playfield is smaller than screen res
	playfield_scale = playfield_width / 512
	scale = height/ 768
	move_right = int(width * 0.2)  # center the playfield
	move_down = int(height * 0.1)
	return playfield_scale, playfield_width, playfield_height, scale, move_right, move_down


def main():

	data = read("config.json")

	skin_path = data["Skin path"]
	beatmap_file = data[".osu path"]
	replay_file = data[".osr path"]
	multi_process = data["Process"]
	codec = data["Video codec"]
	output_path = data["Output path"]
	start_time = data["Start time"]
	end_time = data["End time"]
	ffmpeg = data["ffmpeg path"]
	default_path = data["Default skin path"]
	fps = data["FPS"]
	width = data["Width"]
	height = data["Height"]

	if skin_path[-1] != "/" and skin_path[-1] != "\\":
		skin_path += "/"

	if default_path[-1] != "/" and default_path[-1] != "\\":
		default_path += "/"

	playfield_scale, playfield_width, playfield_height, scale, move_right, move_down = get_screensize(width, height)
	paths = Paths(skin_path, default_path, output_path, ffmpeg)


	skin = Skin(skin_path)
	defaultskin = Skin(default_path)

	SkinPaths.path = skin_path
	SkinPaths.default_path = default_path
	SkinPaths.skin_ini = skin
	SkinPaths.default_skin_ini = defaultskin

	replay_info = osrparse.parse_replay_file(replay_file)
	hr = Mod.HardRock in replay_info.mod_combination
	hd = Mod.Hidden in replay_info.mod_combination

	beatmap = read_file(beatmap_file, playfield_scale, skin.colours, hr)

	replay_event, cur_time = setupReplay(replay_file, beatmap.start_time, beatmap.end_time)
	start_index, end_index = findTime(start_time, end_time, replay_event, cur_time)

	if Mod.DoubleTime in replay_info.mod_combination or Mod.Nightcore in replay_info.mod_combination:
		time_frame = 1500
	elif Mod.HalfTime in replay_info.mod_combination:
		time_frame = 750
	else:
		time_frame = 1000

	settings = Settings(width, height, fps, scale, playfield_scale, playfield_width, playfield_height, move_down, move_right, time_frame)

	endtime_fp = beatmap.hitobjects[-1]["time"] + 800
	beatmap.hitobjects.append(
		{"x": 0, "y": 0, "time": endtime_fp, "combo_number": 0, "type": ["end"]})  # to avoid index out of range

	resultinfo = checkmain(beatmap, replay_info, replay_event, cur_time, settings)
	print(beatmap.diff)

	a = open("map.txt", "w")
	a.write(str(beatmap.hitobjects))
	a.close()
	a = open("resultinfo.txt", "w")
	a.write(str(resultinfo))
	a.close()


	diffcalculator = DiffCalculator(beatmap.diff)
	timepreempt = diffcalculator.ar()
	to_time, hitobjectindex = search_time(start_time, beatmap.hitobjects)
	to_time -= timepreempt
	osr_index = search_osrindex(to_time, replay_event)
	offset = beatmap.hitobjects[hitobjectindex]["time"] - replay_event[osr_index][TIMES]

	a = open("offset.txt", "w")
	a.write(str(offset))
	a.close()

	create_frame(codec, beatmap, skin, paths, replay_event, resultinfo, start_index, end_index, multi_process, settings, hd)
	os.system('"{}" -i {} -codec copy output.mp4 -y'.format(ffmpeg, output_path))


if __name__ == "__main__":
	asdf = time.time()
	main()
	print("\nTotal time:", time.time() - asdf)
