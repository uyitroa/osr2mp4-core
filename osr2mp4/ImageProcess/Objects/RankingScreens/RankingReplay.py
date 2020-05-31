from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen


class RankingReplay(ARankingScreen):
	def __init__(self, frames, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings)

		self.rankingreplay = frames[0]

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			imageproc.add(self.rankingreplay, background, self.settings.width - self.rankingreplay.size[0]/2, 576 * self.settings.scale, self.alpha)
