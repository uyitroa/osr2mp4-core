from ... import imageproc
from ...PrepareFrames.Components.Text import prepare_text


class PPCounter:
	def __init__(self, settings):
		self.settings = settings
		self.frames = []
		self.x = 1270
		self.y = 100
		self.pp = 0
		self.size = 20
		self.color = (100, 255, 255)
		self.alpha = 1
		self.fontpath = ""
		self.gap = 0

		self.loadsettings(settings.ppsettings)
		self.loadimg()
		# self.gap = self.frames["0"].size[0]

	def loadsettings(self, json):
		self.x = json["x"]
		self.y = json["y"]
		self.size = json["size"]
		self.color = tuple(json["rgb"])
		self.alpha = json["alpha"]
		self.fontpath = json["Font"]
		self.gap = json["gap"]

	def loadimg(self):
		char = [str(x) for x in range(10)]
		char.append(".")
		char.append(" ")
		char.append("p")
		self.frames = prepare_text(char, self.size * self.settings.scale, self.color, self.settings, alpha=self.alpha, fontpath=self.fontpath)

	def update_pp(self, pp):
		self.set_pp(pp)

	def set_pp(self, pp):
		self.pp = round(pp, 2)

	def draw_number(self, background):
		pp = str(self.pp)
		x = self.x * self.settings.scale
		y = self.y * self.settings.scale
		for digit in pp:
			imageproc.add(self.frames[digit], background, x, y, self.alpha, topleft=True)
			x += self.frames[digit].size[0] + self.gap * self.settings.scale

	def add_to_frame(self, background):
		"""

		:param background: numpy.array
		:return:
		"""

		if not self.settings.settings["Enable PP counter"]:
			return

		self.draw_number(background)
