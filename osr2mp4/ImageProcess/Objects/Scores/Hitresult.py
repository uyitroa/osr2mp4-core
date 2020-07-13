from ....osrparse.enums import Mod

from ... import imageproc
from ..FrameObject import FrameObject


class HitResult(FrameObject):
	def __init__(self, frames, settings, mods):
		super().__init__(frames, settings=settings)
		self.moveright = self.settings.moveright
		self.movedown = self.settings.movedown
		self.divide_by_255 = 1 / 255.0
		self.hitresults = []
		self.interval = self.settings.timeframe / self.settings.fps
		self.time = 1000
		self.misscount = 0
		self.multiplieranimation = {0: 2, 50: 1, 100: 1, 300: 1}
		self.playfieldscale = self.settings.playfieldscale
		self.showmiss = not (Mod.Relax in mods or Mod.Autopilot in mods)

	def add_result(self, scores, x, y):
		"""
		:param scores: hitresult
		:param x: 0-512
		:param y: 0-384
		:return:
		"""
		x = int(x * self.playfieldscale) + self.moveright
		y = int(y * self.playfieldscale) + self.movedown

		if scores == 0:
			self.misscount += 1
			x -= 10 * self.playfieldscale

		if scores == 300 and self.frames[300][0].size[0] == 1 and self.frames[300][0].size[1] == 1:
			return

		if scores == 0 and not self.showmiss:
			return

		# [score, x, y, index, alpha, time, go down]
		self.hitresults.append([scores, x, y, 0, 40, 0, 3])

	def add_to_frame(self, background):
		i = len(self.hitresults)
		while i > 0:
			i -= 1

			score = self.hitresults[i][0]

			if self.hitresults[i][5] >= self.time * self.multiplieranimation[score]:
				del self.hitresults[i]
				if score == 0:
					self.misscount -= 1
				if self.misscount == 0:  # if there is no misscount then this is the last element so we can break
					break
				else:
					continue

			img = self.frames[score][int(self.hitresults[i][3])]

			x, y = self.hitresults[i][1], self.hitresults[i][2]
			imageproc.add(img, background, x, y, alpha=self.hitresults[i][4] / 100)

			if score == 0:
				self.hitresults[i][2] += self.hitresults[i][6] * self.playfieldscale
				self.hitresults[i][6] = max(0.5, self.hitresults[i][6] - 0.2 * 60/self.settings.fps)

			self.hitresults[i][3] = min(len(self.frames[score]) - 1, self.hitresults[i][3] + 1 * 60/self.settings.fps)
			self.hitresults[i][5] += self.interval * 60/self.settings.fps  #

			if self.hitresults[i][5] >= self.time - self.interval * 20:
				self.hitresults[i][4] = max(0, self.hitresults[i][4] - 5 * 60/self.settings.fps)
			else:
				self.hitresults[i][4] = min(100, self.hitresults[i][4] + 20 * 60/self.settings.fps)

