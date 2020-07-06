from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen


class RankingHitresults(ARankingScreen):
	def __init__(self, frames, replayinfo, numberframes, gap, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings=settings)
		self.replayinfo = replayinfo
		self.numberframes = numberframes
		self.gap = gap * settings.scale
		self.hitresultframes = frames

		# guessed
		self.hitresultx = 135 * settings.scale
		self.hitresulty = 255 * settings.scale
		self.hitresultwidth = 320 * settings.scale
		self.hitresultheight = 95 * settings.scale
		
		self.hitresultgap = 75 * settings.scale
		self.snake = 5 * settings.scale

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
			x += 15 * self.settings.scale
			imageproc.add(frames[11], background, x, y, alpha=alpha)

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.draw_score(str(self.replayinfo.score), background, 175 * self.settings.scale, 150 * self.settings.scale, self.alpha, self.gap - 10 * self.settings.scale)
			self.draw_score(str(self.replayinfo.number_300s), background, self.hitresultx, self.hitresulty, self.alpha)
			self.draw_score(str(self.replayinfo.number_100s), background, self.hitresultx, (self.hitresulty + self.hitresultheight), self.alpha)
			self.draw_score(str(self.replayinfo.number_50s), background, self.hitresultx, (self.hitresulty + self.hitresultheight * 2), self.alpha)

			self.draw_score(str(self.replayinfo.gekis), background, (self.hitresultx + self.hitresultwidth), self.hitresulty, self.alpha)
			self.draw_score(str(self.replayinfo.katus), background, (self.hitresultx + self.hitresultwidth), (self.hitresulty + self.hitresultheight), self.alpha)
			self.draw_score(str(self.replayinfo.misses), background, (self.hitresultx + self.hitresultwidth), (self.hitresulty + self.hitresultheight * 2), self.alpha)

			imageproc.add(self.hitresultframes[300], background, (self.hitresultx - self.hitresultgap), (self.hitresulty - self.snake), alpha=self.alpha)
			imageproc.add(self.hitresultframes[100], background, (self.hitresultx - self.hitresultgap), ((self.hitresulty - self.snake) + self.hitresultheight), alpha=self.alpha)
			imageproc.add(self.hitresultframes[50], background, (self.hitresultx - self.hitresultgap), ((self.hitresulty - self.snake) + self.hitresultheight * 2), alpha=self.alpha)
			imageproc.add(self.hitresultframes[0], background, (self.hitresultx - self.hitresultgap + self.hitresultwidth), ((self.hitresulty - self.snake) + self.hitresultheight * 2), alpha=self.alpha)

			imageproc.add(self.hitresultframes[305], background, (self.hitresultx - self.hitresultgap + self.hitresultwidth), (self.hitresulty - self.snake), alpha=self.alpha)
			imageproc.add(self.hitresultframes[105], background, (self.hitresultx - self.hitresultgap + self.hitresultwidth), ((self.hitresulty - self.snake) + self.hitresultheight), alpha=self.alpha)
