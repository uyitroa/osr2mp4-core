from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen
from ....global_var import Settings


class Menuback(ARankingScreen):
	def __init__(self, frames, skin):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy)

		self.buttonframes = frames
		self.buttonindex = 0

		self.framerate = int(skin.general["AnimationFramerate"])


	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.buttonindex += self.framerate * 1/Settings.fps
			self.buttonindex = self.buttonindex % len(self.buttonframes)

			imageproc.add(self.buttonframes[int(self.buttonindex)], background, 0, Settings.height - self.buttonframes[int(self.buttonindex)].size[1], self.alpha, topleft=True)
