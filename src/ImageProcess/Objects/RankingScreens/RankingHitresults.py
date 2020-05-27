from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen
from ....global_var import Settings


class RankingHitresults(ARankingScreen):
	def __init__(self, frames, replayinfo, numberframes, gap):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy)
		self.replayinfo = replayinfo
		self.numberframes = numberframes
		self.gap = gap * Settings.scale  #int(gap * Settings.scale * 0.5)
		self.hitresultframes = frames

		self.hitresultx = 135
		self.hitresulty = 255
		self.hitresultwidth = 320
		self.hitresultheight = 95
		
		self.hitresultgap = 75
		self.snake = 5

	def draw_score(self, score_string, background, x, y, alpha, gap=None):

		frames = self.numberframes[0]
		if gap is None:
			gap = self.gap
			frames = self.numberframes[1]
			# score_string += "x"

		for digit in score_string:
			if digit == "x":
				index = 11
			else:
				index = int(digit)
			imageproc.add(frames[index], background, x, y, alpha=alpha)
			x += -gap + frames[0].size[0]

		if gap == self.gap:
			x += 15 * Settings.scale
			imageproc.add(frames[11], background, x, y, alpha=alpha)

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.draw_score(str(self.replayinfo.score), background, 180 * Settings.scale, 150 * Settings.scale, self.alpha, self.gap - 10 * Settings.scale)
			self.draw_score(str(self.replayinfo.number_300s), background, self.hitresultx * Settings.scale, self.hitresulty * Settings.scale, self.alpha)
			self.draw_score(str(self.replayinfo.number_100s), background, self.hitresultx * Settings.scale, (self.hitresulty + self.hitresultheight) * Settings.scale, self.alpha)
			self.draw_score(str(self.replayinfo.number_50s), background, self.hitresultx * Settings.scale, (self.hitresulty + self.hitresultheight * 2) * Settings.scale, self.alpha)

			self.draw_score(str(self.replayinfo.gekis), background, (self.hitresultx + self.hitresultwidth)* Settings.scale, self.hitresulty * Settings.scale, self.alpha)
			self.draw_score(str(self.replayinfo.katus), background, (self.hitresultx + self.hitresultwidth) * Settings.scale, (self.hitresulty + self.hitresultheight) * Settings.scale, self.alpha)
			self.draw_score(str(self.replayinfo.misses), background, (self.hitresultx + self.hitresultwidth) * Settings.scale, (self.hitresulty + self.hitresultheight * 2) * Settings.scale, self.alpha)

			imageproc.add(self.hitresultframes[300], background, (self.hitresultx - self.hitresultgap) * Settings.scale, (self.hitresulty - self.snake) * Settings.scale, alpha=self.alpha)
			imageproc.add(self.hitresultframes[100], background, (self.hitresultx - self.hitresultgap) * Settings.scale, ((self.hitresulty - self.snake) + self.hitresultheight) * Settings.scale, alpha=self.alpha)
			imageproc.add(self.hitresultframes[50], background, (self.hitresultx - self.hitresultgap) * Settings.scale, ((self.hitresulty - self.snake) + self.hitresultheight * 2) * Settings.scale, alpha=self.alpha)
			imageproc.add(self.hitresultframes[0], background, (self.hitresultx - self.hitresultgap + self.hitresultwidth) * Settings.scale, ((self.hitresulty - self.snake) + self.hitresultheight * 2) * Settings.scale, alpha=self.alpha)

			imageproc.add(self.hitresultframes[305], background, (self.hitresultx - self.hitresultgap + self.hitresultwidth) * Settings.scale, (self.hitresulty - self.snake) * Settings.scale, alpha=self.alpha)
			imageproc.add(self.hitresultframes[105], background, (self.hitresultx - self.hitresultgap + self.hitresultwidth) * Settings.scale, ((self.hitresulty - self.snake) + self.hitresultheight) * Settings.scale, alpha=self.alpha)
