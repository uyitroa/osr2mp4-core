from osrparse.enums import Mod

from ..Parser.skinparser import Skin
from ..Utils.Resolution import get_screensize
from ..global_var import Settings, Paths, SkinPaths, GameplaySettings


def setupglobals(data, gameplaydata, replay_info):
	skin_path = data["Skin path"]
	beatmap_path = data["Beatmap path"]
	output_path = data["Output path"]
	ffmpeg = data["ffmpeg path"]
	default_path = Paths.path + "res/default/"
	fps = data["FPS"]
	width = data["Width"]
	height = data["Height"]
	osupath = data["osu! path"]

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
	Settings.width, Settings.height, Settings.scale = width, height, scale
	Settings.playfieldscale, Settings.playfieldwidth, Settings.playfieldheight = playfield_scale, playfield_width, playfield_height
	Settings.fps, Settings.timeframe = fps, time_frame
	Settings.moveright, Settings.movedown = move_right, move_down

	Paths.output = output_path
	Paths.ffmpeg = ffmpeg
	Paths.beatmap = beatmap_path
	Paths.osu = osupath


	skin = Skin(skin_path, default_path)
	defaultskin = Skin(default_path, default_path)

	SkinPaths.path = skin_path
	SkinPaths.default_path = default_path
	SkinPaths.skin_ini = skin
	SkinPaths.default_skin_ini = skin

	GameplaySettings.settings = gameplaydata
