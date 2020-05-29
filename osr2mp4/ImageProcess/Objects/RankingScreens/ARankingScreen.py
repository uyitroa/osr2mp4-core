from PIL import Image

from ..FrameObject import FrameObject
from ....global_var import Settings


class ARankingScreen(FrameObject):
	FADEIN = -1
	FADEOUT = 1

	def __init__(self, frames):
		super().__init__(frames)
		self.alpha = 0
		self.fade = self.FADEOUT
		self.drawing = False

	def start_show(self):
		self.drawing = True

	def add_to_frame(self, background):
		if not self.drawing:
			return

		if self.fade == self.FADEOUT:
			self.alpha += Settings.timeframe / Settings.fps * 0.001
			self.alpha = min(1, max(self.alpha, 0))

		if self.alpha >= 1 and self.fade == self.FADEOUT:
			self.fade = self.FADEIN
			self.alpha = 0

		if self.fade == self.FADEIN:
			self.alpha += Settings.timeframe / Settings.fps * 0.001
			self.alpha = min(1, max(self.alpha, 0))
			super().add_to_frame(background, 0, 0, alpha=self.alpha, topleft=True)
