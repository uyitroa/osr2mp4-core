from ..FrameObject import FrameObject


class Sections(FrameObject):
	FAIL = 0
	PASS = 1

	def __init__(self, frames, settings):
		super().__init__(frames, settings=settings)
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
		self.out += 1000/self.settings.fps * 60/self.settings.fps
		self.blink += 60/self.settings.fps
		if self.out < self.blinktime and (self.blink % 5 <= 2):
			return
		if self.out >= self.showtime:
			self.show = False

		alpha = max(0.0, min(1.0, (self.showtime - self.out)/self.fadeouttime))
		super().add_to_frame(background, self.settings.width//2, self.settings.height//2, alpha=alpha)
