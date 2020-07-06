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

		self.codec = None
		self.process = None
		self.enablelog = False
