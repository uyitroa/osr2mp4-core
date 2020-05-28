import inspect
import os
import osrparse
from osrparse.enums import Mod

from .Parser.jsonparser import read
from .AudioProcess.CreateAudio import create_audio
from .CheckSystem.checkmain import checkmain
from .Parser.osrparser import setupReplay
from .Parser.osuparser import read_file
from .Utils.HashBeatmap import get_osu
from .Utils.Setup import setupglobals
from .Utils.Timing import find_time, get_offset
from .VideoProcess.CreateFrames import create_frame
from .VideoProcess.DiskUtils import concat_videos, mix_video_audio, create_dir
from .global_var import Paths, Settings, SkinPaths


class Dummy: pass


class Osr2mp4:
	def __init__(self, data=None, gameplaysettings=None, filedata=None, filesettings=None):
		Paths.path = os.path.dirname(os.path.abspath(inspect.getsourcefile(Dummy)))
		if Paths.path[-1] != "/" and Paths.path[-1] != "\\":
			Paths.path += "/"

		create_dir()  # in case filenotfounderror no such file or directory ../temp/
		if gameplaysettings is None:
			gameplaysettings = {
				"Cursor size": 1,
				"In-game interface": True,
				"Show scoreboard": True,
				"Background dim": 100,
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

		self.data = data
		replaypath = data[".osr path"]
		starttime = data["Start time"]
		endtime = data["End time"]

		self.replay_info = osrparse.parse_replay_file(replaypath)

		upsidedown = Mod.HardRock in self.replay_info.mod_combination

		setupglobals(self.data, gameplaysettings, self.replay_info)

		self.drawers, self.writers, self.pipes = None, None, None
		self.audio = None

		beatmap_file = get_osu(Paths.beatmap, self.replay_info.beatmap_hash)
		self.beatmap = read_file(beatmap_file, Settings.playfieldscale, SkinPaths.skin_ini.colours, upsidedown)

		self.replay_event, self.cur_time = setupReplay(replaypath, self.beatmap)
		self.start_index, self.end_index = find_time(starttime, endtime, self.replay_event, self.cur_time)
		self.starttimne, self.endtime = starttime, endtime

		self.resultinfo = None

	def startvideo(self):
		hd = Mod.Hidden in self.replay_info.mod_combination
		self.drawers, self.writers, self.pipes = create_frame(self.data["Video codec"], self.beatmap,
		                                                      SkinPaths.skin_ini, self.replay_event, self.replay_info,
		                                                      self.resultinfo, self.start_index, self.end_index,
		                                                      self.data["Process"], hd, self.endtime == -1)

	def analyse_replay(self):
		self.resultinfo = checkmain(self.beatmap, self.replay_info, self.replay_event, self.cur_time)

	def startaudio(self):
		dt = Mod.DoubleTime in self.replay_info.mod_combination
		offset, endtime = get_offset(self.beatmap, self.start_index, self.end_index, self.replay_event)
		self.audio = create_audio(self.resultinfo, self.beatmap, offset, endtime, self.beatmap.general["AudioFilename"],
		                          self.data["Process"], dt)

	def startall(self):
		self.analyse_replay()
		self.startaudio()
		self.startvideo()

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
			concat_videos()
		mix_video_audio()
