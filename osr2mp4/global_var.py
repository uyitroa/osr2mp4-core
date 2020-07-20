from .osrparse.enums import Mod


class Settings:

	def __init__(self):
		self.skin_path = None
		self.default_path = None
		self.skin_ini = None
		self.default_skin_ini = None
		self.format = ".png"
		self.x2 = "@2x"

		self.ffmpeg = None
		self.output = None
		self.beatmap = None
		self.osu = None
		self.path = None
		self.temp = None

		self.width = None
		self.height = None
		self.fps = None
		self.scale = None
		self.playfieldscale = None
		self.playfieldwidth = None
		self.playfieldheight = None
		self.movedown = None
		self.moveright = None
		self.timeframe = None

		self.settings = {
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

		self.ppsettings = {
			"x": 1240,
			"y": 725,
			"Size": 25,
			"Rgb": [
				255,
				255,
				255
			],
			"Alpha": 1,
			"Font": "arial.ttf",
			"Background": "",
			"Hitresult x": 50,
			"Hitresult y": 150,
			"Hitresult Size": 16,
			"Hitresult Rgb": [
				255,
				255,
				255
			],
			"Hitresult Alpha": 1,
			"Hitresult Font": "arial.ttf",
			"Hitresult Background": "",
			"Hitresult Gap": 50
		}

		self.codec = None
		self.process = None
		self.enablelog = False


# source: ggjjwp
sortedmods = [
	Mod.NoFail,
	Mod.Easy,
	Mod.Hidden,
	Mod.HardRock,
	Mod.Relax,
	Mod.SuddenDeath,
	Mod.HalfTime,
	Mod.Nightcore,
	Mod.DoubleTime,
	Mod.Flashlight,
	Mod.Perfect,
	Mod.Autopilot,
	Mod.SpunOut,
	Mod.Autoplay
]
