import os

from osr2mp4.osrparse.enums import Mod


defaultsettings = {
	"Cursor size": 1,
	"In-game interface": True,
	"Show scoreboard": True,
	"Show background video": True,
	"Background dim": 100,
	"Background blur": 0,
	"Rotate sliderball": False,
	"Always show key overlay": True,
	"Dont change dim levels during breaks": False,
	"Automatic cursor size": False,
	"Show mods icon": True,
	"Enable PP counter": False,
	"Enable Strain Graph": False,
	"Score meter size": 1,
	"Show score meter": True,
	"Song volume": 50,
	"Effect volume": 50,
	"Ignore beatmap hitsounds": False,
	"Use skin's sound samples": False,
	"Song delay": 0,
	"Global leaderboard": False,
	"Mods leaderboard": "*",
	"Custom mods": "",
	"api key": "lol",
	"Use FFmpeg video writer": False,
	"FFmpeg codec": "libx264",
	"FFmpeg custom commands": "-preset ultrafast -crf 23",
	"Audio bitrate": 500,
	"Slider quality": 2
}

defaultppconfig = {
	"PPCounter": {
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
		"Origin": "right",
		"Background": os.path.join(os.path.dirname(__file__), "res/pptemplate.png"),
	},

	"Hitresult": {
		"x": 50,
		"y": 150,
		"Size": 16,
		"Rgb": [
			255,
			255,
			255
		],
		"Origin": "right",
		"Alpha": 1,
		"Font": "arial.ttf",
		"Background": os.path.join(os.path.dirname(__file__), "res/hitresulttemplate.png"),
		"Gap": 3
	},

	"URCounter": {
		"x": 675,
		"y": 720,
		"Size": 25,
		"Rgb": [
			255,
			255,
			255
		],
		"Origin": "center",
		"Alpha": 1,
		"Font": "arial.ttf",
		"Background": ""
	}
}

defaultstrainconfig = {
	"x": 100,
	"y": 150,
	"Size": 8,
	"AspectRatio": [8,4],
	"Rgb": [255,255,255],
	"Alpha": 1,
	"Smoothing": 5,
	"ProgressAlpha": 0.75,
	"GraphDensity": 30,
}


# source: ggjjwp
sortedmods = [
	Mod.NoFail,
	Mod.Easy,
	Mod.Hidden,
	Mod.HardRock,
	Mod.HardSoft, # dont ask
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


videoextensions = ["mp4", "avi", "mkv", "mov"]


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
		self.resample = None
		self.scale = None
		self.playfieldscale = None
		self.playfieldwidth = None
		self.playfieldheight = None
		self.movedown = None
		self.moveright = None
		self.timeframe = None

		self.strainsettings = defaultstrainconfig
		self.settings = defaultsettings
		self.ppsettings = defaultppconfig

		self.codec = None
		self.audiocodec = None
		self.process = None
		self.enablelog = False

	@property
	def video_fps(self):
		return [self.fps, 60][self.resample]
