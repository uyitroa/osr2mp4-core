from ..FrameObject import FrameObject


class ARankingScreen(FrameObject):
	FADEIN = -1
	FADEOUT = 1

	def __init__(self, frames, settings):
		super().__init__(frames, settings=settings)
		self.alpha = 0
		self.fade = self.FADEOUT
		self.drawing = False
		self.rankx = 0
		self.ranky = 0

	def start_show(self):
		self.drawing = True

	def add_to_frame(self, background):
		if not self.drawing:
			return

		if self.fade == self.FADEOUT:
			self.alpha += self.settings.timeframe / self.settings.fps * 0.001
			self.alpha = min(1, max(self.alpha, 0))

		if self.alpha >= 1 and self.fade == self.FADEOUT:
			self.fade = self.FADEIN
			self.alpha = 0

		if self.fade == self.FADEIN:
			self.alpha += self.settings.timeframe / self.settings.fps * 0.001
			self.alpha = min(1, max(self.alpha, 0))
			super().add_to_frame(background, self.rankx, self.ranky, alpha=self.alpha, topleft=True)
