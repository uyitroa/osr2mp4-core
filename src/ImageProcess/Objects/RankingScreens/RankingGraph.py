from PIL import Image

from ImageProcess import imageproc
from ImageProcess.Objects.RankingScreens.ARankingScreen import ARankingScreen
from global_var import Settings


class RankingGraph(ARankingScreen):
	def __init__(self, frames, replay_info):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy)

		self.rankinggraph = frames[0]

		if replay_info.is_perfect_combo:
			self.rankingperfect = frames[1]
		else:
			self.rankingperfect = Image.new("RGBA", (1, 1))

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			imageproc.add(self.rankinggraph, background, 256 * Settings.scale, 608 * Settings.scale, self.alpha, topleft=True)
			imageproc.add(self.rankingperfect, background, 416 * Settings.scale, 688 * Settings.scale, self.alpha)
