from ..FrameObject import FrameObject


class AScorebar(FrameObject):
	def __init__(self, frames, settings):
		super().__init__(frames, settings=settings)
		self.scrolltime = 100
		self.s = 0
		self.scrolling = False
		self.breakk = None
		self.direction = 1
		self.duration = 0
		self.interval = 0
		self.alpha = 1
		self.h = 0

	def startbreak(self, breakk, duration):
		if self.breakk == breakk["Start"]:
			return
		self.s = 0
		self.scrolling = True
		self.breakk = breakk["Start"]
		self.duration = duration - 100
		self.interval = 1000/self.settings.fps
		self.direction = 0.5 * 60/self.settings.fps

	def animate(self):

		self.duration -= self.interval

		if self.duration < 0:
			self.direction = -0.5 * 60/self.settings.fps
			self.scrolling = True
			self.duration = 0
			self.interval = 0

		# print(self.duration, self.scrolling, alpha, self.s)

		if self.scrolling:
			self.s += 1000/self.settings.fps * self.direction
			self.alpha = min(1.0, max(0.0, 1 - self.s/self.scrolltime))
			self.h = int(self.s * self.settings.fps/1000 * 5)

			if self.alpha == 0 or self.alpha == 1:
				self.scrolling = False

		if not self.scrolling and self.interval == 0:
			self.alpha = 1
			self.h = 0

