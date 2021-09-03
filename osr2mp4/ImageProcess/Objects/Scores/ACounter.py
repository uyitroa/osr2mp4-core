from PIL import Image

from osr2mp4 import logger
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.PrepareFrames.Components.Text import prepare_text


class ACounter:
	def __init__(self, settings: object, countersettings: dict, prefix: str = "PPCounter"):
		self.settings = settings
		self.frames = {}
		self.countersettings = countersettings.get(prefix)
		self.prefix = prefix
		self.background = None
		self.score = ""

		self.loadimg()

	def loadsettings(self, settings: dict):
		self.countersettings = settings[self.prefix]

	def loadimg(self):
		char = [str(x) for x in range(10)]
		char.append(".")
		char.append(" ")
		frames = prepare_text(
			char, 
			self.countersettings["Size"] * self.settings.scale,
			self.countersettings["Rgb"], 
			self.settings,
			alpha=self.countersettings["Alpha"],
			fontpath=self.countersettings["Font"]
			)

		for i in frames:
			self.frames[int(i) if i.isdigit() else i] = frames[i]

		try:
			self.background = Image.open(self.countersettings["Background"]).convert("RGBA")
			scale = self.settings.scale * self.countersettings["Size"]/20
			self.background = imageproc.change_size(self.background, scale, scale)
		except Exception as e:
			logger.error(repr(e))
			self.background = Image.new("RGBA", (1, 1))

	def update(self, score):
		pass

	def set(self, score):
		pass

	def draw_number(self, background):
		x = self.countersettings["x"] * self.settings.scale - self.frames[0].size[0]/2
		y = self.countersettings["y"] * self.settings.scale + self.frames[0].size[1]/2
		origin = self.countersettings.get('Origin', 'right')

		imageproc.draw_number(background, self.score, self.frames, x, y, self.countersettings["Alpha"], origin=origin, gap=0)


	def add_to_frame(self, background):
		"""

		:param background: numpy.array
		:return:
		"""

		if not self.settings.settings["Enable PP counter"]:
			return

		x = self.countersettings["x"] * self.settings.scale
		y = self.countersettings["y"] * self.settings.scale
		imageproc.add(self.background, background, x, y, alpha=self.countersettings["Alpha"])
		self.draw_number(background)
