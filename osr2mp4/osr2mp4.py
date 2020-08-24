import atexit
import inspect
import os
import sys
import time
import traceback

from osr2mp4.osrparse.enums import Mod
from osr2mp4.Utils.getmods import mod_string_to_enums
from osr2mp4.EEnum.EReplay import Replays

from osr2mp4.Utils.Auto import get_auto
from osr2mp4.osrparse import *
import PIL
from osr2mp4.Exceptions import ReplayNotFound, CannotCreateVideo
from osr2mp4.Parser.jsonparser import read
from osr2mp4.AudioProcess.CreateAudio import create_audio
from osr2mp4.CheckSystem.checkmain import checkmain
from osr2mp4.Parser.osrparser import setup_replay, add_useless_shits
from osr2mp4.Parser.osuparser import read_file
from osr2mp4.Utils.HashBeatmap import get_osu
from osr2mp4.Utils.Setup import setupglobals
from osr2mp4.Utils.Timing import find_time, get_offset
from osr2mp4.VideoProcess.CreateFrames import create_frame
from osr2mp4.VideoProcess.DiskUtils import concat_videos, mix_video_audio, setup_dir, cleanup, rename_video
from osr2mp4.global_var import Settings, defaultsettings, defaultppconfig
import uuid
from autologging import traced, logged, TRACE
import logging


class Dummy: pass


def excepthook(exc_type, exc_value, exc_tb):
	tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
	logging.exception(tb)
	print(tb)


@logged(logging.getLogger(__name__))
@traced
class Osr2mp4:

	def __init__(self, data=None, gameplaysettings=None, ppsettings=None,
	             filedata=None, filesettings=None, filepp=None,
	             logtofile=False, enablelog=True, logpath=""):
		self.settings = Settings()
		sys.excepthook = excepthook
		self.settings.path = os.path.dirname(os.path.abspath(inspect.getsourcefile(Dummy)))
		self.settings.path = os.path.relpath(self.settings.path)

		if self.settings.path[-1] != "/" and self.settings.path[-1] != "\\":
			self.settings.path += "/"

		if logpath == "":
			logpath = os.path.join(self.settings.path, "logosr2mp4.log")

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

		self.settings.temp = os.path.join(self.settings.path, str(uuid.uuid1()) + "temp/")

		self.__log.info("test")

		setup_dir(self.settings)

		atexit.register(self.cleanup)

		if gameplaysettings is None:
			gameplaysettings = defaultsettings
		if ppsettings is None:
			ppsettings = defaultppconfig

		if filedata is not None:
			data = read(filedata)
		if filesettings is not None:
			gameplaysettings = read(filesettings)
		if filepp is not None:
			ppsettings = read(filepp)

		if os.path.isdir(data["Output path"]):
			data["Output path"] = os.path.join(data["Output path"], "output.avi")
		self.data = data
		replaypath = data[".osr path"]
		starttime = data["Start time"]
		endtime = data["End time"]

		self.settings.codec = data["Video codec"]
		self.settings.audiocodec = data.get("Audio codec", "aac")
		self.settings.process = data["Process"]

		apikey = gameplaysettings["api key"]
		gameplaysettings["api key"] = None  # avoid logging api key

		self.drawers, self.writers, self.pipes, self.sharedarray = None, None, None, None
		self.audio = None

		self.auto = auto = replaypath == "auto"

		gameplaysettings["Custom mods"] = gameplaysettings.get("Custom mods", "")

		self.replayedit = False

		if not auto:

			try:
				self.replay_info = parse_replay_file(replaypath)
			except FileNotFoundError as e:
				raise ReplayNotFound() from None

			reverse_replay = False

			if gameplaysettings["Custom mods"] != "":
				self.replayedit = True
				original = self.replay_info.mod_combination
				self.replay_info.mod_combination = mod_string_to_enums(gameplaysettings["Custom mods"])
				if Mod.HardRock in self.replay_info.mod_combination and Mod.HardRock not in original:
					reverse_replay = True
				if Mod.HardRock not in self.replay_info.mod_combination and Mod.HardRock in original:
					reverse_replay = True

			setupglobals(self.data, gameplaysettings, self.replay_info.mod_combination, self.settings, ppsettings=ppsettings)

			self.beatmap_file = get_osu(self.settings.beatmap, self.replay_info.beatmap_hash)

			self.beatmap = read_file(self.beatmap_file, self.settings.playfieldscale, self.settings.skin_ini.colours, mods=self.replay_info.mod_combination, lazy=False)

			self.replay_event, self.cur_time = setup_replay(replaypath, self.beatmap, reverse=reverse_replay)
			self.replay_info.play_data = self.replay_event

		else:
			gameplaysettings["Custom mods"] = gameplaysettings.get("Custom mods", "")
			mod_combination = mod_string_to_enums(gameplaysettings["Custom mods"])
			setupglobals(self.data, gameplaysettings, mod_combination, self.settings, ppsettings=ppsettings)

			self.beatmap_file = self.settings.beatmap
			self.settings.beatmap = os.path.dirname(self.settings.beatmap)
			self.beatmap = read_file(self.beatmap_file, self.settings.playfieldscale, self.settings.skin_ini.colours, mods=mod_combination, lazy=False)
			self.replay_info = get_auto(self.beatmap)
			self.replay_info.mod_combination = mod_combination
			add_useless_shits(self.replay_info.play_data, self.beatmap)
			self.cur_time = self.replay_info.play_data[0][Replays.TIMES]
			self.replay_event = self.replay_info.play_data

		self.start_index, self.end_index = find_time(starttime, endtime, self.replay_event, self.settings)
		self.starttimne, self.endtime = starttime, endtime

		self.resultinfo = None

		self.previousprogress = 0

		logging.log(TRACE, "Settings vars {}".format(vars(self.settings)))
		gameplaysettings["api key"] = apikey  # restore api key

	def startvideo(self):
		if self.resultinfo is None:
			self.analyse_replay()
		videotime = (self.start_index, self.end_index)

		if not os.path.isdir(os.path.dirname(os.path.abspath(self.settings.output))):
			raise CannotCreateVideo()

		self.drawers, self.writers, self.pipes, self.sharedarray = create_frame(self.settings, self.beatmap,
		                                                                        self.replay_info, self.resultinfo,
		                                                                        videotime, self.endtime == -1)

	def analyse_replay(self):

		if self.replayedit:
			# remove score limiter
			self.replay_info.score = float("inf")

		self.resultinfo = checkmain(self.beatmap, self.replay_info, self.settings)

		if self.auto or self.replayedit:
			self.replay_info.score = self.resultinfo[-1].score
			self.replay_info.max_combo = self.resultinfo[-1].maxcombo
			self.replay_info.number_300s = self.resultinfo[-1].accuracy[300]
			self.replay_info.number_100s = self.resultinfo[-1].accuracy[100]
			self.replay_info.number_50s = self.resultinfo[-1].accuracy[50]
			self.replay_info.misses = self.resultinfo[-1].accuracy[0]

			self.replay_info.gekis = self.replay_info.number_300s//3 # TODO: LOL
			self.replay_info.katus = self.replay_info.number_100s//3 # TODO: LOL

	def startaudio(self):
		if self.resultinfo is None:
			self.analyse_replay()
		offset, endtime = get_offset(self.beatmap, self.start_index, self.end_index, self.replay_info, self.endtime)
		self.audio = create_audio(self.resultinfo, self.beatmap, offset, endtime, self.settings, self.replay_info.mod_combination)

	def startall(self):
		self.analyse_replay()
		self.startvideo()
		self.startaudio()

	def joinvideo(self):
		if self.data["Process"] >= 1:
			for i in range(self.data["Process"]):
				logging.debug(self.drawers[i].is_alive())
				logging.debug(self.writers[i].is_alive())
				self.drawers[i].join()
				logging.debug(f"Joined drawers {i}")

				self.writers[i].join()  # temporary fixm might cause some infinite loop
				logging.debug(f"Joined writers {i}")

				conn1, conn2 = self.pipes[i]
				conn1.close()
				conn2.close()
				logging.debug(f"Closed conn {i}")

		self.drawers, self.writers, self.pipes = None, None, None

	def joinaudio(self):
		self.audio.join()
		self.audio = None

	def joinall(self):
		if self.drawers is not None:
			self.joinvideo()
		if self.audio is not None:
			self.joinaudio()

		if self.data["Process"] > 1:
			concat_videos(self.settings)
		elif self.data["Process"] == 1:
			rename_video(self.settings)
		mix_video_audio(self.settings)

	def cleanup(self):
		try:
			if self.drawers is not None:
				for x in range(len(self.drawers)):
					self.drawers[x].terminate()
					self.writers[x].terminate()
					conn1, conn2 = self.pipes[x]
					conn1.close()
					conn2.close()
			if self.audio is not None:
				self.audio.terminate()
		except Exception as e:
			logging.error(repr(e))
		cleanup(self.settings)

	def getprogress(self):
		should_continue = os.path.isfile(os.path.join(self.settings.temp, "speed.txt"))
		if not should_continue:
			return 0

		fileopen = open(os.path.join(self.settings.temp, "speed.txt"), "r")
		try:
			info = fileopen.read().split("\n")
			framecount = int(info[0])
			deltatime = float(info[1])
			filename = info[2]
			starttime = float(info[3])

			curdeltatime = time.time() - starttime
			estimated_curframe = curdeltatime / deltatime * framecount

			estimated_progress = estimated_curframe / (self.end_index - self.start_index)
		except ValueError:
			if "done" in info:
				estimated_progress = 100
			else:
				estimated_progress = self.previousprogress

		self.previousprogress = estimated_progress
		fileopen.close()
		return min(99, estimated_progress * 100)
