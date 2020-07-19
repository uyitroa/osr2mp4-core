import logging

from PIL import Image

from ... import imageproc
from ...PrepareFrames.Components.Text import prepare_text


class ACounter:
	def __init__(self, settings, countersettings, prefix=""):
		self.settings = settings
		self.frames = {}
		self.countersettings = countersettings
		self.background = None
		self.prefix = prefix
		self.score = ""

		self.loadsettings(settings.ppsettings)
		self.loadimg()

	def loadsettings(self, countersettings):
		countersettings[self.prefix + "Rgb"] = tuple(countersettings[self.prefix + "Rgb"])
		self.countersettings = countersettings

	def loadimg(self):
		char = [str(x) for x in range(10)]
		char.append(".")
		char.append(" ")
		self.frames = prepare_text(char, self.countersettings[self.prefix + "Size"] * self.settings.scale,
		                           self.countersettings[self.prefix + "Rgb"], self.settings,
		                           alpha=self.countersettings[self.prefix + "Alpha"],
		                           fontpath=self.countersettings[self.prefix + "Font"])

		try:
			self.background = Image.open(self.countersettings[self.prefix + "Background"]).convert("RGBA")
			scale = self.settings.scale * self.countersettings[self.prefix + "Size"]/20
			self.background = imageproc.change_size(self.background, scale, scale)
		except Exception as e:
			logging.error(repr(e))
			self.background = Image.new("RGBA", (1, 1))

	def update(self, score):
		pass

	def set(self, score):
		pass

	def draw_number(self, background):
		x = self.countersettings[self.prefix + "x"] * self.settings.scale
		y = self.countersettings[self.prefix + "y"] * self.settings.scale
		for digit in self.score[::-1]:
			x -= self.frames[digit].size[0]
			imageproc.add(self.frames[digit], background, x, y, self.countersettings[self.prefix + "Alpha"], topleft=True)

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
