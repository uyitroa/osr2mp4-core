from PIL import Image

from ImageProcess import imageproc
from ImageProcess.Objects.RankingScreens.ARankingScreen import ARankingScreen
from global_var import Settings


class RankingAccuracy(ARankingScreen):
	def __init__(self, frames, replayinfo, numberframes, gap):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy)
		maxscore = (replayinfo.number_300s + replayinfo.number_100s + replayinfo.number_50s + replayinfo.misses) * 300
		score = replayinfo.number_300s * 300 + replayinfo.number_100s * 100 + replayinfo.number_50s * 50
		self.accuracy = str(round(score/maxscore * 100, 2))

		self.numberframes = numberframes[1]
		self.gap = int(gap * Settings.scale * 0.5)

		self.accuracyframes = frames
		self.accuracyindex = 0


	def draw_score(self, score_string, background, x, y, alpha):
		score_string += "%"
		for digit in score_string:
			if digit == ".":
				index = 10
			elif digit == "%":
				index = 12
			else:
				index = int(digit)
			imageproc.add(self.numberframes[index], background, x, y, alpha=alpha)
			x += -self.gap + self.numberframes[index].size[0]

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.draw_score(self.accuracy, background, 325 * Settings.scale, 560 * Settings.scale, self.alpha)

			self.accuracyindex += 1000/Settings.fps
			self.accuracyindex = self.accuracyindex % len(self.accuracyframes)

			imageproc.add(self.accuracyframes[int(self.accuracyindex)], background, 291 * Settings.scale, 608 * Settings.scale, self.alpha, topleft=True)
