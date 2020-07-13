import ctypes
import glob
import inspect
from multiprocessing.sharedctypes import RawArray

from PIL import Image

import bruh
from osr2mp4.CheckSystem.checkmain import checkmain
from osr2mp4.Utils.Timing import find_time

from osr2mp4.VideoProcess.AFrames import PreparedFrames

from osr2mp4.Utils.HashBeatmap import get_osu
from osr2mp4.osrparse.enums import Mod

from osr2mp4.Utils.Setup import setupglobals

from osr2mp4.Parser import jsonparser

from osr2mp4.AudioProcess.Utils import getfilenames
from osr2mp4.Parser.osrparser import setupReplay
from osr2mp4.Parser.osuparser import read_file
from osr2mp4.Parser.skinparser import Skin
from osr2mp4 import osr2mp4
from osr2mp4.osrparse import *
import os


class Dummy: pass


abspath = os.path.dirname(os.path.abspath(inspect.getsourcefile(Dummy)))
# abspath = os.path.relpath(abspath)
if abspath[-1] != "/" and abspath[-1] != "\\":
	abspath += "/"
abspath += "resources/"


def getinfos(mapname, upsidedown=False):
	bmap = getbeatmap(mapname, upsidedown)

	replay_infos = []
	should_continue = True
	x = 0
	fname = ''
	while should_continue:
		replay_event, cur_time = setupReplay("{}{}{}.osr".format(abspath, mapname, fname), bmap)
		replay_info = parse_replay_file("{}{}{}.osr".format(abspath, mapname, fname))
		replay_info.play_data = replay_event
		replay_infos.append(replay_info)

		x += 1
		fname = str(x)
		should_continue = os.path.isfile("{}{}{}.osr".format(abspath, mapname, fname))

	return bmap, replay_infos


def getbeatmap(mapname, upsidedown=False):
	skin = Skin("{}".format(abspath), "{}".format(abspath))
	bmap = read_file("{}{}.osu".format(abspath, mapname), 1, skin.colours, upsidedown)
	return bmap


def getlistfromtxt(filename):
	a = open(filename, "r")
	mylist = eval(a.read())
	a.close()
	return mylist


def getaudiofilename(mapname):
	bmap = getbeatmap(mapname)
	resultlist = getfilenames(bmap, False)
	expectedlist = getlistfromtxt(abspath + mapname + "expect.txt")
	return [list(resultlist[0].keys()), list(resultlist[1].keys())], expectedlist


def setupenv(suffix, mapname):
	from osr2mp4.global_var import Settings
	settings = Settings()
	config = jsonparser.read("{}config{}.json".format(abspath, suffix))
	gameplayconfig = jsonparser.read("{}settings{}.json".format(abspath, suffix))
	replay_info = parse_replay_file("{}{}.osr".format(abspath, mapname))

	settings.path = os.path.dirname(os.path.abspath(inspect.getsourcefile(osr2mp4.Dummy)))
	settings.path = os.path.relpath(settings.path)
	if settings.path[-1] != "/" and settings.path[-1] != "\\":
		settings.path += "/"

	config["Skin path"] = abspath + config["Skin path"]
	config["Beatmap path"] = abspath + mapname
	config[".osr path"] = abspath + mapname + ".osr"

	setupglobals(config, gameplayconfig, replay_info, settings)
	beatmap_file = get_osu(settings.beatmap, replay_info.beatmap_hash)
	beatmap = read_file(beatmap_file, settings.playfieldscale, settings.skin_ini.colours,
	                    Mod.HardRock in replay_info.mod_combination)
	return settings, replay_info, beatmap


def updateframes(resultprefix, frames):
	images = vars(frames)
	for f in images:
		imglist = getattr(frames, f)
		while type(imglist).__name__ == "list" or type(imglist).__name__ == "tuple":
			index = max(0, (len(imglist) - 1) // 2)  # check the middle image
			imglist = imglist[index]

		if type(imglist).__name__ == "Image":
			print("Updating {}".format(resultprefix + f + ".png"))
			imglist.save(resultprefix + f + ".png")


def getframes(suffix, mapname, update=False, data=None):
	if data is None:
		settings, replay_info, beatmap = setupenv(suffix, mapname)
	else:
		settings, replay_info, beatmap = data
	frames = PreparedFrames(settings, beatmap, Mod.Hidden in replay_info.mod_combination)
	resultprefix = abspath + "frames/" + suffix + mapname
	if update:
		updateframes(resultprefix, frames)
	return resultprefix, frames


def getdrawer(suffix, mapname, videotime):
	from osr2mp4.VideoProcess.Draw import Drawer
	settings, replay_info, beatmap = setupenv(suffix, mapname)
	replay_event, cur_time = setupReplay("{}{}.osr".format(abspath, mapname), beatmap)
	replay_info.play_data = replay_event
	_, frames = getframes(suffix, mapname, data=(settings, replay_info, beatmap))

	videotime = find_time(*videotime, replay_info.play_data, settings)

	resultinfo = checkmain(beatmap, replay_info, settings, tests=True)

	shared = RawArray(ctypes.c_uint8, settings.height * settings.width * 4)
	drawer = Drawer(shared, beatmap, frames, replay_info, resultinfo, videotime, settings)

	resultprefix = abspath + "frames/" + suffix + mapname
	return resultprefix, drawer, shared


def getexpect(suffix, mapname):
	path = abspath + "orignalframes/" + mapname + "expect" + suffix

	fileopen = open(path + ".txt", "r")
	text = fileopen.read()
	timestamp = int(text.strip())
	videotime = (timestamp / 1000 - 3, timestamp / 1000 + 3)

	fileopen.close()

	try:
		fileopen = open(path + "epsilon.txt", "r")
		text = fileopen.read()
		epsilon = float(text.strip())

		fileopen.close()
	except FileNotFoundError:
		epsilon = 500
	return path, videotime, timestamp, epsilon


def getrightconfigs(suffix):
	config = jsonparser.read("{}config{}.json".format(abspath, suffix))
	settings = jsonparser.read("{}settings{}.json".format(abspath, suffix))

	config["Skin path"] = abspath + config["Skin path"]
	config["Beatmap path"] = abspath + config["Beatmap path"]
	config[".osr path"] = abspath + config[".osr path"]

	config["Output path"] = suffix + config["Output path"]

	return config, settings


def get_length(filename):
	import subprocess
	result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
	                         "format=duration", "-of",
	                         "default=noprint_wrappers=1:nokey=1", filename],
	                        stdout=subprocess.PIPE,
	                        stderr=subprocess.STDOUT)
	return float(result.stdout)


def get_res(filename):
	import cv2
	vid = cv2.VideoCapture(filename)
	height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
	width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

	return width, height


def getskins():
	skinpath = os.path.join(abspath, "skininis", "*.ini")
	return glob.glob(skinpath)
