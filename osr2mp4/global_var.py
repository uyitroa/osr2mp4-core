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
	temp = None


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
