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

		self.width = 1
		self.height = 1
		self.fps = 60
		self.scale = 0
		self.playfieldscale = 0
		self.playfieldwidth = 1
		self.playfieldheight = 1
		self.movedown = 0
		self.moveright = 0
		self.timeframe = 1000

		self.settings = {
					"Cursor size": 1,
					"In-game interface": True,
					"Show scoreboard": True,
					"Background dim": 100,
					"Rotate sliderball": False,
					"Always show key overlay": True,
					"Automatic cursor size": False,
					"Enable PP counter": False,
					"Score meter size": 1,
					"Song volume": 50,
					"Effect volume": 50,
					"Ignore beatmap hitsounds": False,
					"Use skin's sound samples": False,
					"Global leaderboard": False,
					"Mods leaderboard": "*",
					"api key": "lol"
				}

		self.codec = None
		self.process = None
		self.enablelog = False
