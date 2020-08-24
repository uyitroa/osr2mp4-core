from osr2mp4.ImageProcess import imageproc

from osr2mp4.ImageProcess.Objects.Scores.ACounter import ACounter


class HitresultCounter(ACounter):
	def __init__(self, settings):
		super().__init__(settings, settings.ppsettings, prefix="Hitresult ")
		self.score = {100: 0, 50: 0, 0: 0}

	def loadsettings(self, countersettings):
		super().loadsettings(countersettings)

	def update(self, score):
		self.set(score)

	def set(self, score):
		self.score = score

	def draw_number(self, background):
		counter = 0
		gap = self.countersettings["Hitresult Gap"] * self.countersettings["Hitresult Size"]
		for n in self.score:
			if n == 300:
				continue
			x = (self.countersettings[self.prefix + "x"] + gap * counter) * self.settings.scale - self.frames[0].size[0]/2
			y = self.countersettings[self.prefix + "y"] * self.settings.scale + self.frames[0].size[1]/2
			imageproc.draw_number(background, self.score[n], self.frames, x, y, self.countersettings["Hitresult Alpha"], origin="right", gap=0)
			counter += 1
