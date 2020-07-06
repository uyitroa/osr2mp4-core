from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen


class RankingCombo(ARankingScreen):
	def __init__(self, frames, replayinfo, numberframes, gap, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings=settings)
		self.maxcombo = str(replayinfo.max_combo)
		self.numberframes = numberframes[1]
		self.gap = gap * self.settings.scale
		self.comboframes = frames
		self.comboindex = 0


		if self.settings.skin_ini.general["Version"] == 1:
			self.y = 500
		else:
			self.y = 480


	def draw_score(self, score_string, background, x, y, alpha):
		for digit in score_string:
			if digit == "x":
				index = 11
			else:
				index = int(digit)
			imageproc.add(self.numberframes[index], background, x, y, alpha=alpha)
			x += -self.gap + self.numberframes[index].size[0]
		x += 15 * self.settings.scale
		imageproc.add(self.numberframes[11], background, x, y, alpha=alpha)

	def add_to_frame(self, background):
		# source: https://osu.ppy.sh/help/wiki/Skinning/Interface#ranking-screen
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.draw_score(self.maxcombo, background, 30 * self.settings.scale, 552 * self.settings.scale, self.alpha)

			self.comboindex += 1000/self.settings.fps
			self.comboindex = self.comboindex % len(self.comboframes)

			imageproc.add(self.comboframes[int(self.comboindex)], background, 8 * self.settings.scale, self.y * self.settings.scale, self.alpha, topleft=True)
