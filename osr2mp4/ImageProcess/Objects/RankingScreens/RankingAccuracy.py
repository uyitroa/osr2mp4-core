from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen


class RankingAccuracy(ARankingScreen):
	def __init__(self, frames, replayinfo, numberframes, gap, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings=settings)
		maxscore = (replayinfo.number_300s + replayinfo.number_100s + replayinfo.number_50s + replayinfo.misses) * 300
		score = replayinfo.number_300s * 300 + replayinfo.number_100s * 100 + replayinfo.number_50s * 50
		self.accuracy = str("{:.2f}".format(score/maxscore * 100))

		self.numberframes = numberframes[1]
		self.gap = gap * self.settings.scale

		self.accuracyframes = frames
		self.accuracyindex = 0

		if settings.skin_ini.general["Version"] == 1:
			self.y = 500
		else:
			self.y = 480


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
		# source: https://osu.ppy.sh/help/wiki/Skinning/Interface#ranking-screen
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.draw_score(self.accuracy, background, 325 * self.settings.scale, 552 * self.settings.scale, self.alpha)

			self.accuracyindex += 1000/self.settings.fps
			self.accuracyindex = self.accuracyindex % len(self.accuracyframes)

			imageproc.add(self.accuracyframes[int(self.accuracyindex)], background, 291 * self.settings.scale, self.y * self.settings.scale, self.alpha, topleft=True)
