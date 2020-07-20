import logging

from autologging import traced, logged

from ..global_var import Settings
from ..osrparse.enums import Mod

from ..Parser.skinparser import Skin
from ..Utils.Resolution import get_screensize


@logged(logging.getLogger(__name__))
@traced
def setupglobals(data, gameplaydata, replay_info, settings, ppsettings=None):
	skin_path = data["Skin path"]
	beatmap_path = data["Beatmap path"]
	output_path = data.get("Output path", "output.avi")
	ffmpeg = data.get("ffmpeg path", "ffmpeg")
	default_path = settings.path + "res/default/"
	fps = data.get("FPS", 60)
	width = data.get("Width", 1920)
	height = data.get("Height", 1080)
	osupath = data.get("osu! path", None)

	if skin_path[-1] != "/" and skin_path[-1] != "\\":
		skin_path += "/"

	if beatmap_path[-1] != "/" and beatmap_path[-1] != "\\":
		beatmap_path += "/"

	if osupath[-1] != "/" and osupath[-1] != "\\":
		osupath += "/"

	if Mod.DoubleTime in replay_info.mod_combination or Mod.Nightcore in replay_info.mod_combination:
		time_frame = 1500
	elif Mod.HalfTime in replay_info.mod_combination:
		time_frame = 750
	else:
		time_frame = 1000

	playfield_scale, playfield_width, playfield_height, scale, move_right, move_down = get_screensize(width, height)
	settings.width, settings.height, settings.scale = width, height, scale
	settings.playfieldscale, settings.playfieldwidth, settings.playfieldheight = playfield_scale, playfield_width, playfield_height
	settings.fps, settings.timeframe = fps, time_frame
	settings.moveright, settings.movedown = move_right, move_down

	settings.output = output_path
	settings.ffmpeg = ffmpeg
	settings.beatmap = beatmap_path
	settings.osu = osupath

	skin = Skin(skin_path, default_path)
	# defaultskin = Skin(default_path, default_path)

	settings.skin_path = skin_path
	settings.default_path = default_path
	settings.skin_ini = skin
	settings.default_skin_ini = skin

	gameplaydata["Enable PP counter"] = gameplaydata.get("Enable PP counter", False)
	gameplaydata["Song delay"] = gameplaydata.get("Song delay", 0)
	gameplaydata["Show mods icon"] = gameplaydata.get("Show mods icon", True)
	settings.settings = gameplaydata

	if ppsettings is not None:
		settings.ppsettings = ppsettings


