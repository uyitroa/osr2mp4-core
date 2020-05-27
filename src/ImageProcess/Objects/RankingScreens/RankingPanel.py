from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen
from ....global_var import Settings


class RankingPanel(ARankingScreen):
	FADEIN = -1
	FADEOUT = 1

	def __init__(self, frames):
		super().__init__(frames)
		self.backgroundimg = Image.new("RGBA", (Settings.width, Settings.height), (0, 0, 0, 255))

	def add_to_frame(self, background):

		if not self.drawing:
			return

		if self.fade == self.FADEOUT:
			imageproc.add(self.backgroundimg, background, 0, 0, alpha=self.alpha, topleft=True)
		super().add_to_frame(background)
