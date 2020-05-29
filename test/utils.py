from osr2mp4.AudioProcess.Utils import getfilenames
from osr2mp4.Parser.osrparser import setupReplay
from osr2mp4.Parser.osuparser import read_file
from osr2mp4.Parser.skinparser import Skin
import osrparse
import os


def getinfos(path, mapname, upsidedown=False):
	bmap = getbeatmap(mapname, path, upsidedown)

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


def getbeatmap(mapname, path, upsidedown=False):
	skin = Skin("{}".format(path), "{}".format(path))
	bmap = read_file("{}{}.osu".format(path, mapname), 1, skin.colours, upsidedown)
	return bmap


def getlistfromtxt(filename):
	a = open(filename, "r")
	mylist = eval(a.read())
	a.close()
	return mylist


def getaudiofilename(mapname, path):
	bmap = getbeatmap(mapname, path)
	resultlist = getfilenames(bmap, False)
	expectedlist = getlistfromtxt(path + mapname + "expect.txt")
	return resultlist, expectedlist

