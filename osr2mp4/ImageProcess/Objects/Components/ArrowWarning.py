from ..FrameObject import FrameObject


class ArrowWarning(FrameObject):
	def __init__(self, frames, settings):
		super().__init__(frames, settings=settings)
		self.timer = 0
		self.breakk = None

		self.left = int(settings.width * 0.1)
		self.right = int(settings.width * 0.9)
		self.up = int(settings.height * 0.2)
		self.down = int(settings.height * 0.8)

	def startbreak(self, breakk):
		if self.breakk == breakk:
			return
		self.breakk = breakk
		self.timer = 0

	def add_to_frame(self, background, cur_time):

		if self.timer > 40:
			return

		if self.breakk is None or cur_time < self.breakk:
			return

		self.timer += 60/self.settings.fps
		if self.timer % 8 >= 4:
			return

		self.frame_index = 0
		super().add_to_frame(background, self.left, self.down)
		super().add_to_frame(background, self.left, self.up)
		self.frame_index = 1
		super().add_to_frame(background, self.right, self.down)
		super().add_to_frame(background, self.right, self.up)

