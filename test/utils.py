from Parser.osrparser import setupReplay
from Parser.osuparser import read_file
from Parser.skinparser import Skin
import osrparse
import os


def getinfos(path, mapname, upsidedown=False):
	skin = Skin("{}".format(path), "{}".format(path))
	bmap = read_file("{}{}.osu".format(path, mapname), 1, skin.colours, upsidedown)

	replays = []
	replay_infos = []
	should_continue = True
	x = 0
	fname = ''
	while should_continue:
		replay_event, cur_time = setupReplay("{}{}{}.osr".format(path, mapname, fname), bmap)
		replays.append(replay_event)
		replay_info = osrparse.parse_replay_file("{}{}{}.osr".format(path, mapname, fname))
		replay_infos.append(replay_info)

		x += 1
		fname = str(x)
		should_continue = os.path.isfile("{}{}{}.osr".format(path, mapname, fname))

	return bmap, replays, replay_infos
