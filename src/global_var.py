class SkinPaths:
	path = None
	default_path = None
	skin_ini = None
	default_skin_ini = None
	format = ".png"
	x2 = "@2x"


class Paths:
	ffmpeg = None
	output = None
	beatmap = None
	osu = None
	path = None


class Settings:
	width = None
	height = None
	fps = None
	scale = None
	playfieldscale = None
	playfieldwidth = None
	playfieldheight = None
	movedown = None
	moveright = None
	timeframe = None


class GameplaySettings:
	settings = {
		"Cursor size": 1,
		"In-game interface": 1,
		"Show scoreboard": 1,
		"Background dim": 100,
		"Always show key overlay": 1,
		"Automatic cursor size": 0,
		"Score meter size": 1,
		"Song volume": 100,
		"Effect volume": 100,
		"Ignore beatmap hitsounds": 0
	}