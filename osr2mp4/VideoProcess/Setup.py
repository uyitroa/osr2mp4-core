import numpy as np
from PIL import Image
from recordclass import recordclass
from ..CheckSystem.Judgement import DiffCalculator
from ..EEnum.EReplay import Replays
from ..InfoProcessor import Updater
from ..Utils.skip import skip
from .AFrames import FrameObjects
from ..global_var import Settings, SkinPaths, Paths, GameplaySettings

FrameInfo = recordclass("FrameInfo", "cur_time index_hitobj info_index osr_index index_fp obj_endtime x_end y_end, break_index")
CursorEvent = recordclass("CursorEvent", "event old_x old_y")


def get_buffer(img):
	np_img = np.frombuffer(img, dtype=np.uint8)
	np_img = np_img.reshape((Settings.height, Settings.width, 4))
	pbuffer = Image.frombuffer("RGBA", (Settings.width, Settings.height), np_img, 'raw', "RGBA", 0, 1)
	pbuffer.readonly = False
	return np_img, pbuffer


def setup_global(settings, paths, skinpaths, gameplaysettings):
	Settings.width, Settings.height, Settings.scale = settings[0], settings[1], settings[2]
	Settings.playfieldscale, Settings.playfieldwidth, Settings.playfieldheight = settings[3], settings[4], settings[5]
	Settings.fps, Settings.timeframe = settings[6], settings[7]
	Settings.moveright, Settings.movedown = settings[8], settings[9]

	SkinPaths.path = skinpaths[0]
	SkinPaths.default_path = skinpaths[1]
	SkinPaths.skin_ini = skinpaths[2]
	SkinPaths.default_skin_ini = skinpaths[3]

	Paths.output = paths[0]
	Paths.ffmpeg = paths[1]
	Paths.beatmap = paths[2]
	Paths.osu = paths[3]
	Paths.path = paths[4]

	GameplaySettings.settings = gameplaysettings


def getlist():
	settings = []
	paths = []
	skinpaths = []

	settings.extend([Settings.width, Settings.height, Settings.scale])
	settings.extend([Settings.playfieldscale, Settings.playfieldwidth, Settings.playfieldheight])
	settings.extend([Settings.fps, Settings.timeframe])
	settings.extend([Settings.moveright, Settings.movedown])

	skinpaths.append(SkinPaths.path)
	skinpaths.append(SkinPaths.default_path)
	skinpaths.append(SkinPaths.skin_ini)
	skinpaths.append(SkinPaths.default_skin_ini)

	paths.append(Paths.output)
	paths.append(Paths.ffmpeg)
	paths.append(Paths.beatmap)
	paths.append(Paths.osu)
	paths.append(Paths.path)

	return settings, paths, skinpaths


def setup_draw(beatmap, frames, replay_event, replay_info, resultinfo, shared, skin, start_index, hd):
	old_cursor_x = int(replay_event[0][Replays.CURSOR_X] * Settings.playfieldscale) + Settings.moveright
	old_cursor_y = int(replay_event[0][Replays.CURSOR_Y] * Settings.playfieldscale) + Settings.moveright

	diffcalculator = DiffCalculator(beatmap.diff)

	time_preempt = diffcalculator.ar()

	component = FrameObjects(frames, skin, beatmap, replay_info, diffcalculator, hd)

	component.cursor_trail.set_cursor(old_cursor_x, old_cursor_y, replay_event[0][Replays.TIMES])

	preempt_followpoint = 800

	updater = Updater(resultinfo, component)

	simulate = replay_event[start_index][Replays.TIMES]
	frame_info = FrameInfo(*skip(simulate, resultinfo, replay_event, beatmap, time_preempt, component))

	print(start_index, frame_info.osr_index)
	component.background.startbreak(beatmap.breakperiods[frame_info.break_index], frame_info.cur_time)

	cursor_event = CursorEvent(replay_event[frame_info.osr_index], old_cursor_x, old_cursor_y)

	updater.info_index = frame_info.info_index

	img = Image.new("RGB", (1, 1))
	np_img, pbuffer = get_buffer(shared)


	return component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater
