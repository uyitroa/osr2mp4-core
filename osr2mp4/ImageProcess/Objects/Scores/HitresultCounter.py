from ... import imageproc

from .ACounter import ACounter


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
		for n in self.score:
			if n == 300:
				continue
			x = (self.countersettings[self.prefix + "x"] + self.countersettings["Hitresult Gap"] * counter) * self.settings.scale
			y = self.countersettings[self.prefix + "y"] * self.settings.scale
			for digit in str(self.score[n]):
				imageproc.add(self.frames[digit], background, x, y, self.countersettings["Hitresult Alpha"], topleft=True)
				x += self.frames[digit].size[0]
			counter += 1
