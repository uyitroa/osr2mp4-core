from ..FrameObject import FrameObject


class Number(FrameObject):
	def __init__(self, frames, fonts):
		super().__init__(frames[0])
		self.nwidth = self.w()
		scale = frames[1]
		self.overlap = int(fonts["HitCircleOverlap"]*scale)
		print(self.overlap, fonts["HitCircleOverlap"], scale)

	def add_to_frame(self, background, x, y, alpha, number):
		"""
		:param background: PIL.Image
		:param x: int
		:param y: int
		:param alpha: alpha index frame of circle
		:param number: int
		:return:
		"""
		number = str(number)
		size = (self.nwidth - self.overlap) * (len(number) - 1)
		x_pos = x - size//2
		y_pos = y

		for digit in number:
			self.frame_index = int(digit)
			super().add_to_frame(background, x_pos, y_pos, alpha=alpha/100)
			x_pos += -self.overlap + self.nwidth
