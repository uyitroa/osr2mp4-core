from PIL import Image

from ImageProcess import imageproc
from ImageProcess.Objects.RankingScreens.ARankingScreen import ARankingScreen
from global_var import Settings


class RankingCombo(ARankingScreen):
	def __init__(self, frames, replayinfo, numberframes, gap):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy)
		self.maxcombo = str(replayinfo.max_combo)
		self.numberframes = numberframes[1]
		self.gap = int(gap * Settings.scale * 0.5)
		self.comboframes = frames
		self.comboindex = 0


	def draw_score(self, score_string, background, x, y, alpha):
		for digit in score_string:
			if digit == "x":
				index = 11
			else:
				index = int(digit)
			imageproc.add(self.numberframes[index], background, x, y, alpha=alpha)
			x += -self.gap + self.numberframes[index].size[0]
		x += 15 * Settings.scale
		imageproc.add(self.numberframes[11], background, x, y, alpha=alpha)

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.draw_score(self.maxcombo, background, 30 * Settings.scale, 560 * Settings.scale, self.alpha)

			self.comboindex += 1000/Settings.fps
			self.comboindex = self.comboindex % len(self.comboframes)

			imageproc.add(self.comboframes[int(self.comboindex)], background, 8 * Settings.scale, 500 * Settings.scale, self.alpha, topleft=True)
