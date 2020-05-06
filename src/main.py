import hashlib
import os

import osrparse
from osrparse.enums import Mod
from recordclass import recordclass

from AudioProcess.main import processAudio
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
from global_var import Settings, Paths
from skip import search_time, search_osrindex


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


def get_offset(beatmap, start_index, start_time, replay_event):
	diffcalculator = DiffCalculator(beatmap.diff)
	timepreempt = diffcalculator.ar()
	to_time, hitobjectindex = search_time(start_time*1000, beatmap.hitobjects)
	to_time -= timepreempt
	osr_index = search_osrindex(to_time, replay_event)
	index = max(osr_index, start_index)
	# print(replay_event[osr_index][TIMES], replay_event[start_index][TIMES], replay_event[index][TIMES])
	offset = replay_event[index][TIMES]

	return offset


def get_osu(path, maphash):
	filelist = os.listdir(path)
	for f in filelist[:]:
		if f.endswith(".osu"):
			md5 = hashlib.md5()
			with open(path+f, 'rb') as b:
				while True:
					data = b.read(1)
					if not data:
						break
					md5.update(data)
			m = md5.hexdigest()
			if maphash == m:
				return path+f



def main():

	data = read("config.json")

	skin_path = data["Skin path"]
	beatmap_path = data["Beatmap path"]
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

	if beatmap_path[-1] != "/" and beatmap_path[-1] != "\\":
		beatmap_path += "/"

	Paths.output = output_path
	Paths.ffmpeg = ffmpeg


	skin = Skin(skin_path)
	defaultskin = Skin(default_path)

	SkinPaths.path = skin_path
	SkinPaths.default_path = default_path
	SkinPaths.skin_ini = skin
	SkinPaths.default_skin_ini = defaultskin

	replay_info = osrparse.parse_replay_file(replay_file)
	hr = Mod.HardRock in replay_info.mod_combination
	hd = Mod.Hidden in replay_info.mod_combination
	if Mod.DoubleTime in replay_info.mod_combination or Mod.Nightcore in replay_info.mod_combination:
		time_frame = 1500
	elif Mod.HalfTime in replay_info.mod_combination:
		time_frame = 750
	else:
		time_frame = 1000


	beatmap_file = get_osu(beatmap_path, replay_info.beatmap_hash)

	playfield_scale, playfield_width, playfield_height, scale, move_right, move_down = get_screensize(width, height)
	Settings.width, Settings.height, Settings.scale = width, height, scale
	Settings.playfieldscale, Settings.playfieldwidth, Settings.playfieldheight = playfield_scale, playfield_width, playfield_height
	Settings.fps, Settings.timeframe = fps, time_frame
	Settings.moveright, Settings.movedown = move_right, move_down


	beatmap = read_file(beatmap_file, playfield_scale, skin.colours, hr)

	print("Timing:", beatmap.timing_point[0]["Offset"])
	replay_event, cur_time = setupReplay(replay_file, beatmap)
	start_index, end_index = findTime(start_time, end_time, replay_event, cur_time)

	endtime_fp = beatmap.hitobjects[-1]["time"] + 800

	beatmap.hitobjects.append({"x": 0, "y": 0, "time": endtime_fp, "combo_number": 0, "type": ["end"]})  # to avoid index out of range

	resultinfo = checkmain(beatmap, replay_info, replay_event, cur_time)
	print(beatmap.diff)


	offset = get_offset(beatmap, start_index, start_time, replay_event)

	processAudio(resultinfo, beatmap.hitobjects, skin_path, offset, default_path, beatmap_path, beatmap.general["AudioFilename"])

	create_frame(codec, beatmap, skin, replay_event, resultinfo, start_index, end_index, multi_process, hd)

	f = Paths.output[:-4] + "f" + Paths.output[-4:]
	os.system('"{}" -i "{}" -i z.mp3 -c:v copy -c:a aac "{}" -y'.format(ffmpeg, f, output_path))
	os.system('"{}" -i "{}" -codec copy output.mp4 -y'.format(ffmpeg, output_path))


if __name__ == "__main__":
	asdf = time.time()
	main()
	print("\nTotal time:", time.time() - asdf)
