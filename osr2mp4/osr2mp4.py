import atexit
import inspect
import os
import sys
import time
import osrparse
from osrparse.enums import Mod
import PIL
from .Exceptions import ReplayNotFound
from .Parser.jsonparser import read
from .AudioProcess.CreateAudio import create_audio
from .CheckSystem.checkmain import checkmain
from .Parser.osrparser import setupReplay
from .Parser.osuparser import read_file
from .Utils.HashBeatmap import get_osu
from .Utils.Setup import setupglobals
from .Utils.Timing import find_time, get_offset
from .VideoProcess.CreateFrames import create_frame
from .VideoProcess.DiskUtils import concat_videos, mix_video_audio, setup_dir, cleanup
from .global_var import Settings
import uuid
from autologging import traced, logged, TRACE
import logging


class Dummy: pass


# logging.basicConfig(
# 	level=TRACE, stream=open("test.log", "w"),
# 	format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")


@logged(logging.getLogger(__name__))
@traced
class Osr2mp4:

	def __init__(self, data=None, gameplaysettings=None, filedata=None, filesettings=None, logtofile=False, enablelog=True, logpath=""):
		self.settings = Settings()
		self.settings.path = os.path.dirname(os.path.abspath(inspect.getsourcefile(Dummy)))
		self.settings.path = os.path.relpath(self.settings.path)

		if self.settings.path[-1] != "/" and self.settings.path[-1] != "\\":
			self.settings.path += "/"

		if logpath == "":
			logpath = self.settings.path + "logosr2mp4.log"

		if logtofile:
			logging.basicConfig(
				level=TRACE, stream=open(logpath, "w"),
				format="%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s")
			logging.getLogger(PIL.__name__).setLevel(logging.WARNING)
		else:
			logging.basicConfig(
				level=TRACE, stream=sys.stdout,
				format="%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s")
			logging.getLogger(PIL.__name__).setLevel(logging.WARNING)

		if not enablelog:
			logging.basicConfig(level=logging.CRITICAL, stream=os.devnull)

		self.settings.enablelog = enablelog

		# else:
		# 	logging.basicConfig(
		# 		level=logging.CRITICAL, stream=open(self.settings.path + "logs/test.log", "w"),
		# 		format="%(levelname)s:%(name)s:%(funcName)s:%(message)s")

		self.settings.temp = self.settings.path + str(uuid.uuid1()) + "temp/"

		self.__log.info("test")

		setup_dir(self.settings)

		atexit.register(self.cleanup)

		if gameplaysettings is None:
			gameplaysettings = {
				"Cursor size": 1,
				"In-game interface": True,
				"Show scoreboard": True,
				"Background dim": 100,
				"Rotate sliderball": False,
				"Always show key overlay": True,
				"Automatic cursor size": False,
				"Score meter size": 1,
				"Song volume": 50,
				"Effect volume": 50,
				"Ignore beatmap hitsounds": False,
				"Use skin's sound samples": False,
				"Global leaderboard": False,
				"Mods leaderboard": "*",
				"api key": "lol"
			}

		if filedata is not None:
			data = read(filedata)
		if filesettings is not None:
			gameplaysettings = read(filesettings)
		if os.path.isdir(data["Output path"]):
			data["Output path"] = os.path.join(data["Output path"], "output.avi")
		self.data = data
		replaypath = data[".osr path"]
		starttime = data["Start time"]
		endtime = data["End time"]

		self.settings.codec = data["Video codec"]
		self.settings.process = data["Process"]

		try:
			self.replay_info = osrparse.parse_replay_file(replaypath)
		except FileNotFoundError as e:
			raise ReplayNotFound() from None
		#
		upsidedown = Mod.HardRock in self.replay_info.mod_combination

		setupglobals(self.data, gameplaysettings, self.replay_info, self.settings)

		self.drawers, self.writers, self.pipes, self.sharedarray = None, None, None, None
		self.audio = None

		beatmap_file = get_osu(self.settings.beatmap, self.replay_info.beatmap_hash)
		self.beatmap = read_file(beatmap_file, self.settings.playfieldscale, self.settings.skin_ini.colours, upsidedown)

		self.replay_event, self.cur_time = setupReplay(replaypath, self.beatmap)
		self.replay_info.play_data = self.replay_event
		self.start_index, self.end_index = find_time(starttime, endtime, self.replay_event, self.settings)
		self.starttimne, self.endtime = starttime, endtime

		self.resultinfo = None

		self.previousprogress = 0

		logging.log(TRACE, "Settings vars {}".format(vars(self.settings)))

	def startvideo(self):
		if self.resultinfo is None:
			self.analyse_replay()
		videotime = (self.start_index, self.end_index)
		self.drawers, self.writers, self.pipes, self.sharedarray = create_frame(self.settings, self.beatmap, self.replay_info, self.resultinfo, videotime, self.endtime == -1)

	def analyse_replay(self):
		self.resultinfo = checkmain(self.beatmap, self.replay_info, self.settings)

	def startaudio(self):
		if self.resultinfo is None:
			self.analyse_replay()
		offset, endtime = get_offset(self.beatmap, self.start_index, self.end_index, self.replay_event, self.endtime)
		self.audio = create_audio(self.resultinfo, self.beatmap, offset, endtime, self.settings, self.replay_info.mod_combination)

	def startall(self):
		self.analyse_replay()
		self.startvideo()
		self.startaudio()

	def joinvideo(self):
		if self.data["Process"] >= 1:
			for i in range(self.data["Process"]):
				self.drawers[i].join()
				conn1, conn2 = self.pipes[i]
				conn1.close()
				conn2.close()
				self.writers[i].join()

		self.drawers, self.writers, self.pipes = None, None, None

	def joinaudio(self):
		self.audio.join()
		self.audio = None

	def joinall(self):
		if self.drawers is not None:
			self.joinvideo()
		if self.audio is not None:
			self.joinaudio()

		if self.data["Process"] >= 1:
			concat_videos(self.settings)
		mix_video_audio(self.settings)

	def cleanup(self):
		if self.drawers is not None:
			for x in range(len(self.drawers)):
				self.drawers[x].terminate()
				self.writers[x].terminate()
				conn1, conn2 = self.pipes[x]
				conn1.close()
				conn2.close()
		if self.audio is not None:
			self.audio.terminate()
		cleanup(self.settings)

	def getprogress(self):
		should_continue = os.path.isfile(self.settings.temp + "speed.txt")
		if not should_continue:
			return 0

		fileopen = open(self.settings.temp + "speed.txt", "r")
		try:
			info = fileopen.read().split("\n")
			framecount = int(info[0])
			deltatime = float(info[1])
			filename = info[2]
			starttime = float(info[3])

			curdeltatime = time.time() - starttime
			estimated_curframe = curdeltatime/deltatime * framecount

			estimated_progress = estimated_curframe/(self.end_index - self.start_index)
		except ValueError:
			if "done" in info:
				estimated_progress = 100
			else:
				estimated_progress = self.previousprogress

		self.previousprogress = estimated_progress
		fileopen.close()
		return min(99, estimated_progress * 100)
