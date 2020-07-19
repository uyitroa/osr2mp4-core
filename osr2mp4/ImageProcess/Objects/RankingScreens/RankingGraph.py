from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen


class RankingGraph(ARankingScreen):
	def __init__(self, frames, replay_info, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings=settings)

		self.rankinggraph = frames[0]

		if replay_info.is_perfect_combo:
			self.rankingperfect = frames[1]
		else:
			self.rankingperfect = Image.new("RGBA", (1, 1))

		self.rankingur = frames[2]

		# source: https://osu.ppy.sh/help/wiki/Skinning/Interface#ranking-screen
		if self.settings.skin_ini.general["Version"] == 1:
			self.y = 576
			self.perfectx = 320
		else:
			self.y = 608
			self.perfectx = 416

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			imageproc.add(self.rankinggraph, background, 256 * self.settings.scale, self.y * self.settings.scale, self.alpha, topleft=True)
			imageproc.add(self.rankingperfect, background, self.perfectx * self.settings.scale, 688 * self.settings.scale, self.alpha)
			imageproc.add(self.rankingur, background, (self.perfectx+100) * self.settings.scale, 688 * self.settings.scale, self.alpha ** 10)
