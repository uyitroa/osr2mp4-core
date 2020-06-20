from PIL import Image

from ... import imageproc
from .ARankingScreen import ARankingScreen


class Menuback(ARankingScreen):
	def __init__(self, frames, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings=settings)

		self.buttonframes = frames
		self.buttonindex = 0

		self.framerate = int(settings.skin_ini.general["AnimationFramerate"])


	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.buttonindex += self.framerate * 1/self.settings.fps
			self.buttonindex = self.buttonindex % len(self.buttonframes)

			imageproc.add(self.buttonframes[int(self.buttonindex)], background, 0, self.settings.height - self.buttonframes[int(self.buttonindex)].size[1], self.alpha, topleft=True)
