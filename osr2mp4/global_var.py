import os

from .osrparse.enums import Mod


defaultsettings = {
	"Cursor size": 1,
	"In-game interface": True,
	"Show scoreboard": True,
	"Background dim": 100,
	"Rotate sliderball": False,
	"Always show key overlay": True,
	"Automatic cursor size": False,
	"Show mods icon": True,
	"Enable PP counter": False,
	"Score meter size": 1,
	"Song volume": 50,
	"Effect volume": 50,
	"Ignore beatmap hitsounds": False,
	"Use skin's sound samples": False,
	"Song delay": 0,
	"Global leaderboard": False,
	"Mods leaderboard": "*",
	"api key": "lol",
}

defaultppconfig = {
	"x": 1320,
	"y": 725,
	"Size": 25,
	"Rgb": [
		255,
		255,
		255
	],
	"Alpha": 1,
	"Font": "arial.ttf",
	"Background": os.path.join(os.path.dirname(__file__), "res/pptemplate.png"),
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
	"Hitresult Background": os.path.join(os.path.dirname(__file__), "res/hitresulttemplate.png"),
	"Hitresult Gap": 3
}


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

		self.settings = defaultsettings

		self.ppsettings = defaultppconfig

		self.codec = None
		self.process = None
		self.enablelog = False
