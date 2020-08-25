from osr2mp4.ImageProcess.Animation.easing import easingoutcubic

from osr2mp4.osrparse.enums import Mod

from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.Objects.FrameObject import FrameObject


class HitResult(FrameObject):
	def __init__(self, frames, settings, mods):
		super().__init__(frames[0], settings=settings)
		self.moveright = self.settings.moveright
		self.movedown = self.settings.movedown
		self.divide_by_255 = 1 / 255.0
		self.hitresults = []
		self.interval = self.settings.timeframe / self.settings.fps
		self.time = 1500
		self.misscount = 0
		self.multiplieranimation = {0: 2, 50: 1, 100: 1, 300: 1}
		self.playfieldscale = self.settings.playfieldscale
		self.showmiss = not (Mod.Relax in mods or Mod.Autopilot in mods)
		self.singleframemiss = frames[1]

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

		ynitial = y
		if scores == 0 and self.singleframemiss:
			ynitial = y - 40 * self.settings.playfieldscale

		# [score, x, y, index, alpha, time, go down]
		self.hitresults.append([scores, x, ynitial, 0, 40, 0, y])

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

			if score == 0 and self.singleframemiss:
				current = self.settings.timeframe/self.settings.fps
				change = self.hitresults[i][6] - self.hitresults[i][2]
				duration = 1000

				self.hitresults[i][2] = easingoutcubic(current, self.hitresults[i][2], change, duration)

			self.hitresults[i][3] = min(len(self.frames[score]) - 1, self.hitresults[i][3] + 1 * 60/self.settings.fps)
			self.hitresults[i][5] += self.interval

			if self.hitresults[i][5] >= self.time - 500:
				self.hitresults[i][4] = max(0, (self.time - self.hitresults[i][5])/500 * 100)
			else:
				self.hitresults[i][4] = min(100, self.hitresults[i][4] + 20 * 60/self.settings.fps)

