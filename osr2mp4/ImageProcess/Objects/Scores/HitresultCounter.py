from osr2mp4.ImageProcess import imageproc

from osr2mp4.ImageProcess.Objects.Scores.ACounter import ACounter


class HitresultCounter(ACounter):
	def __init__(self, settings):
		super().__init__(settings, settings.ppsettings, prefix="Hitresult")
		self.score = {100: 0, 50: 0, 0: 0}

	def update(self, score):
		self.set(score)

	def set(self, score):
		self.score = score

	def draw_number(self, background):
		counter = 0
		gap = self.countersettings[self.prefix + "Gap"] * self.countersettings[self.prefix + "Size"]
		origin = self.countersettings.get(self.prefix + 'Origin', 'right')

		for n in self.score:
			if n == 300:
				continue

			x = (self.countersettings[self.prefix + "x"] + gap * counter) * self.settings.scale - self.frames[0].size[0]/2
			y = self.countersettings[self.prefix + "y"] * self.settings.scale + self.frames[0].size[1]/2
			imageproc.draw_number(background, self.score[n], self.frames, x, y, self.countersettings[self.prefix + "Alpha"], origin=origin, gap=0)
			counter += 1
