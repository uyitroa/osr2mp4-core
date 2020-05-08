from ImageProcess.Objects.FrameObject import FrameObject
from global_var import Settings


class Scorebar(FrameObject):
	def __init__(self, frames):
		super().__init__(frames)
		self.scrolltime = 100
		self.s = 0
		self.scrolling = False
		self.breakk = None
		self.direction = 1
		self.duration = 0
		self.interval = 0
		self.alpha = 1
		self.h = 5

	def startbreak(self, breakk, duration):
		if self.breakk == breakk:
			return
		self.s = 0
		self.scrolling = True
		self.breakk = breakk
		self.duration = duration - 100
		self.interval = 1000/Settings.fps
		self.direction = 0.5

	def add_to_frame(self, background):

		self.duration -= self.interval

		if self.duration < 0:
			self.direction = -0.5
			self.scrolling = True
			self.duration = 0
			self.interval = 0

		# print(self.duration, self.scrolling, alpha, self.s)

		if self.scrolling:
			self.s += 1000/Settings.fps * self.direction
			self.alpha = min(1.0, max(0.0, 1 - self.s/self.scrolltime))
			self.h = int(self.s * Settings.fps/1000 * 5)

			if self.alpha == 0 or self.alpha == 1:
				self.scrolling = False

		if not self.scrolling and self.interval == 0:
			self.alpha = 1
			self.h = 5

		# print(self.duration, self.scrolling, alpha, self.s, "\n")
		super().add_to_frame(background, 0, -self.h, alpha=self.alpha, topleft=True)
