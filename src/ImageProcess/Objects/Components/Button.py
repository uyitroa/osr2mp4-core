from ImageProcess import imageproc
from ImageProcess.Objects.FrameObject import FrameObject


class ScoreEntry(FrameObject):
	def __init__(self, frames):
		super().__init__(frames)

	def add_to_frame(self, background, x_offset, y_offset, number, index=0):
		number = str(number)
		n = len(number) - 1
		x_start = x_offset - int(n/2 * self.frames[0][index+n].size[0])
		for digit in number:
			digit = int(digit)
			imageproc.add(self.frames[digit][index+n], background, x_start, y_offset)
			x_start += self.frames[digit][index+n].size[0]


class InputOverlay(FrameObject):
	def __init__(self, button_frames, scoreentry):
		"""
		:param button_frames: [PIL.Image]
		:param scoreentry: ScoreEntry(FrameObject)
		"""
		super().__init__(button_frames)
		self.freeze = 0
		self.scoreentry = scoreentry

		self.holding = False
		self.oldclick = True

		self.n = 0

	def set_freeze(self, freeze, n):
		self.freeze = freeze
		self.n = n

	def clicked(self, cur_time):
		if not self.oldclick:
			self.oldclick = True
			if cur_time >= self.freeze:
				self.n += 1
			self.frame_index = 1

		self.holding = True

	def add_to_frame(self, background, x_offset, y_offset, alpha=1):
		if self.holding:
			self.frame_index += 1
			if self.frame_index >= len(self.frames):
				self.frame_index -= 1

		else:
			self.oldclick = False
			self.frame_index -= 1
			if self.frame_index < 0:
				self.frame_index += 1

		self.holding = False
		super().add_to_frame(background, x_offset, y_offset, alpha)
		self.scoreentry.add_to_frame(background, x_offset, y_offset, self.n,
		                             self.frame_index)


class InputOverlayBG(FrameObject):
	def add_to_frame(self, background, x_offset, y_offset):
		# special y_offset
		y_offset = y_offset + self.frames[0].size[1]//2
		super().add_to_frame(background, x_offset, y_offset)
