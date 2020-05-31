import numpy as np
from PIL import Image
from recordclass import recordclass

FrameInfo = recordclass("FrameInfo", "cur_time index_hitobj info_index osr_index index_fp obj_endtime x_end y_end, break_index")
CursorEvent = recordclass("CursorEvent", "event old_x old_y")


def get_buffer(img, settings):
	np_img = np.frombuffer(img, dtype=np.uint8)
	np_img = np_img.reshape((settings.height, settings.width, 4))
	pbuffer = Image.frombuffer("RGBA", (settings.width, settings.height), np_img, 'raw', "RGBA", 0, 1)
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
	Paths.temp = paths[5]

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
	paths.append(Paths.temp)

	return settings, paths, skinpaths
