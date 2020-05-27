from ..FrameObject import FrameObject
from ....global_var import Settings


class Sections(FrameObject):
	FAIL = 0
	PASS = 1

	def __init__(self, frames):
		super().__init__(frames)
		self.frame_index = self.PASS
		self.out = 0
		self.show = False
		self.fadeouttime = 400
		self.blinktime = 200
		self.showtime = 900
		self.blink = 0
		self.breakk = None

	def startbreak(self, status, breakk, hp):
		if self.breakk == breakk:
			return
		self.breakk = breakk
		self.frame_index = status
		self.out = 0
		self.blink = 0
		self.show = True
		if hp < 0.5:
			self.frame_index = self.FAIL
		else:
			self.frame_index = self.PASS

	def add_to_frame(self, background):
		if not self.show:
			return
		self.out += 1000/Settings.fps * 60/Settings.fps
		self.blink += 60/Settings.fps
		if self.out < self.blinktime and (self.blink % 5 <= 2):
			return
		if self.out >= self.showtime:
			self.show = False

		alpha = max(0.0, min(1.0, (self.showtime - self.out)/self.fadeouttime))
		super().add_to_frame(background, Settings.width//2, Settings.height//2, alpha=alpha)
