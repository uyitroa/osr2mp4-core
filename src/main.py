import os

import osrparse
from osrparse.enums import Mod

from AudioProcess.CreateAudio import create_audio
from CheckSystem.checkmain import checkmain
from ImageProcess.PrepareFrames.YImage import SkinPaths
from Parser.jsonparser import read
from Parser.osrparser import setupReplay
from Utils.HashBeatmap import get_osu
from Utils.Setup import setupglobals
from Utils.Timing import get_offset, find_time
from VideoProcess.DiskUtils import mix_video_audio, convert_tomp4, cleanup, concat_videos
from VideoProcess.CreateFrames import create_frame
from Parser.osuparser import *
import time

# const
from global_var import Settings, Paths


def main():

	data = read("config.json")
	replay_file = data[".osr path"]
	multi_process = data["Process"]
	codec = data["Video codec"]
	start_time = data["Start time"]
	end_time = data["End time"]


	replay_info = osrparse.parse_replay_file(replay_file)

	upsidedown = Mod.HardRock in replay_info.mod_combination
	hd = Mod.Hidden in replay_info.mod_combination
	dt = Mod.DoubleTime in replay_info.mod_combination
	print(replay_info.timestamp)
	print(replay_info.number_300s)
	print(replay_info.number_100s)
	print(replay_info.number_50s)
	print(replay_info.misses)
	print(replay_info.score)

	setupglobals(data, replay_info)

	beatmap_file = get_osu(Paths.beatmap, replay_info.beatmap_hash)

	beatmap = read_file(beatmap_file, Settings.playfieldscale, SkinPaths.skin_ini.colours, upsidedown)

	replay_event, cur_time = setupReplay(replay_file, beatmap)

	start_index, end_index = find_time(start_time, end_time, replay_event, cur_time)


	resultinfo = checkmain(beatmap, replay_info, replay_event, cur_time)
	print(resultinfo[-1].accuracy)

	offset, endtime = get_offset(beatmap, start_index, end_index, replay_event)

	audio = create_audio(resultinfo, beatmap, offset, endtime, beatmap.general["AudioFilename"], multi_process, dt)
	drawers, writers, pipes = create_frame(codec, beatmap, SkinPaths.skin_ini, replay_event, replay_info, resultinfo, start_index, end_index, multi_process, hd, end_time == -1)


	if multi_process >= 1:
		audio.join()
		for i in range(multi_process):
			drawers[i].join()
			conn1, conn2 = pipes[i]
			conn1.close()
			conn2.close()
			writers[i].join()

		concat_videos()

	mix_video_audio()

	if os.name != 'nt':
		convert_tomp4()

	cleanup()


if __name__ == "__main__":
	asdf = time.time()
	main()
	print("\nTotal time:", time.time() - asdf)