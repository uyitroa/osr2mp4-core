from ImageProcess import imageproc
from ImageProcess.Objects.FrameObject import FrameObject
from global_var import Settings


class HitResult(FrameObject):
	def __init__(self, frames):
		super().__init__(frames)
		self.moveright = Settings.moveright
		self.movedown = Settings.movedown
		self.divide_by_255 = 1 / 255.0
		self.hitresults = []
		self.interval = Settings.timeframe / Settings.fps
		self.time = 600
		self.playfieldscale = Settings.playfieldscale

	def add_result(self, scores, x, y):
		"""
		:param scores: hitresult
		:param x: 0-512
		:param y: 0-384
		:return:
		"""
		x = int(x * self.playfieldscale) + self.moveright
		y = int(y * self.playfieldscale) + self.movedown

		if scores == 300:
			return
		# [score, x, y, index, alpha, time, go down]
		self.hitresults.append([scores, x, y, 0, 40, 0, 3])

	def add_to_frame(self, background):
		i = len(self.hitresults)
		while i > 0:
			i -= 1
			if self.hitresults[i][5] >= self.time:
				del self.hitresults[i]
				break

			score = self.hitresults[i][0]
			img = self.frames[score][self.hitresults[i][3]]

			x, y = self.hitresults[i][1], self.hitresults[i][2]
			imageproc.add(img, background, x, y, alpha=self.hitresults[i][4] / 100)

			if score == 0:
				self.hitresults[i][2] += int(self.hitresults[i][6] * self.playfieldscale)
				self.hitresults[i][6] = max(0.8, self.hitresults[i][6] - 0.2)

			self.hitresults[i][3] = min(len(self.frames[score]) - 1, self.hitresults[i][3] + 1)
			self.hitresults[i][5] += self.interval

			if self.hitresults[i][5] >= self.time - self.interval * 10:
				self.hitresults[i][4] = max(0, self.hitresults[i][4] - 10)
			else:
				self.hitresults[i][4] = min(100, self.hitresults[i][4] + 20)
