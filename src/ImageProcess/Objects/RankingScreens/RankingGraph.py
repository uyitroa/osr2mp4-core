from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen
from ....global_var import Settings, SkinPaths


class RankingGraph(ARankingScreen):
	def __init__(self, frames, replay_info):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy)

		self.rankinggraph = frames[0]

		if replay_info.is_perfect_combo:
			self.rankingperfect = frames[1]
		else:
			self.rankingperfect = Image.new("RGBA", (1, 1))


		if SkinPaths.skin_ini.general["Version"] == 1:
			self.y = 576
			self.perfectx = 320
		else:
			self.y = 608
			self.perfectx = 416

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			imageproc.add(self.rankinggraph, background, self.perfectx * Settings.scale, self.y * Settings.scale, self.alpha, topleft=True)
			imageproc.add(self.rankingperfect, background, self.perfectx * Settings.scale, 688 * Settings.scale, self.alpha)
