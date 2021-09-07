from PIL import Image

from osr2mp4 import logger
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.PrepareFrames.Components.Text import prepare_text


class ACounter:
	def __init__(self, settings: object, countersettings: dict, prefix: str = ""):
		self.settings = settings
		self.frames = {}
		self.countersettings = countersettings
		self.prefix = prefix + ' ' if prefix else ''
		self.background = None
		self.score = ""

		self.loadimg()

	def loadsettings(self, settings: dict):
		...
		# self.countersettings = settings[self.prefix] # FireRedz: reverted to old format cuz im retarded and cant make it work with osr2mp4 app

	def loadimg(self):
		char = [str(x) for x in range(10)]
		char.append(".")
		char.append(" ")
		frames = prepare_text(
			char, 
			self.countersettings[self.prefix + "Size"] * self.settings.scale,
			self.countersettings[self.prefix + "Rgb"],
			self.settings,
			alpha=self.countersettings[self.prefix + "Alpha"],
			fontpath=self.countersettings[self.prefix + "Font"]
			)

		for i in frames:
			self.frames[int(i) if i.isdigit() else i] = frames[i]

		try:
			self.background = Image.open(self.countersettings[self.prefix + "Background"]).convert("RGBA")
			scale = self.settings.scale * self.countersettings[self.prefix + "Size"]/20
			self.background = imageproc.change_size(self.background, scale, scale)
		except Exception as e:
			logger.error(repr(e))
			self.background = Image.new("RGBA", (1, 1))

	def update(self, score):
		pass

	def set(self, score):
		pass

	def draw_number(self, background):
		x = self.countersettings[self.prefix + "x"] * self.settings.scale - self.frames[0].size[0]/2
		y = self.countersettings[self.prefix + "y"] * self.settings.scale + self.frames[0].size[1]/2
		origin = self.countersettings.get(self.prefix + 'Origin', 'right')

		imageproc.draw_number(background, self.score, self.frames, x, y, self.countersettings[self.prefix + "Alpha"], origin=origin, gap=0)


	def add_to_frame(self, background):
		"""

		:param background: numpy.array
		:return:
		"""

		if not self.settings.settings["Enable PP counter"]:
			return

		x = self.countersettings[self.prefix + "x"] * self.settings.scale
		y = self.countersettings[self.prefix + "y"] * self.settings.scale
		imageproc.add(self.background, background, x, y, alpha=self.countersettings[self.prefix + "Alpha"])
		self.draw_number(background)
