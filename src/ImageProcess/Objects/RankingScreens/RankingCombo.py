from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen
from ....global_var import Settings, SkinPaths


class RankingCombo(ARankingScreen):
	def __init__(self, frames, replayinfo, numberframes, gap):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy)
		self.maxcombo = str(replayinfo.max_combo)
		self.numberframes = numberframes[1]
		self.gap = gap * Settings.scale
		self.comboframes = frames
		self.comboindex = 0


		if SkinPaths.skin_ini.general["Version"] == 1:
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
		x += 15 * Settings.scale
		imageproc.add(self.numberframes[11], background, x, y, alpha=alpha)

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.draw_score(self.maxcombo, background, 30 * Settings.scale, 552 * Settings.scale, self.alpha)

			self.comboindex += 1000/Settings.fps
			self.comboindex = self.comboindex % len(self.comboframes)

			imageproc.add(self.comboframes[int(self.comboindex)], background, 8 * Settings.scale, self.y * Settings.scale, self.alpha, topleft=True)
