from ... import imageproc
from ..FrameObject import FrameObject


class ScoreEntry(FrameObject):
	def __init__(self, frames, settings):
		super().__init__(frames, settings=settings)

	def add_to_frame(self, background, x_offset, y_offset, number, index=0):
		if not self.settings.settings["Always show key overlay"]:
			return

		number = str(number)
		n = len(number) - 1
		index = max(0, min(len(self.frames[0]) - 1, index+n-1))
		x_start = x_offset - int(n/2 * self.frames[0][index].size[0])
		for digit in number:
			digit = int(digit)
			imageproc.add(self.frames[digit][index], background, x_start, y_offset)
			x_start += self.frames[digit][index].size[0]


class InputOverlay(FrameObject):
	def __init__(self, button_frames, scoreentry, settings):
		"""
		:param button_frames: [PIL.Image]
		:param scoreentry: ScoreEntry(FrameObject)
		"""
		super().__init__(button_frames, settings=settings)
		self.freeze = 0
		self.scoreentry = scoreentry

		self.holding = False
		self.oldclick = False

		self.n = 0

	def set_freeze(self, freeze, n):
		self.freeze = freeze
		self.n = n

	def clicked(self, cur_time):
		if not self.oldclick:
			if cur_time < self.freeze:
				return
			self.oldclick = True
			self.n += 1
			self.frame_index = 1

		self.holding = True

	def add_to_frame(self, background, x_offset, y_offset, curtime, alpha=1):
		if background.size[0] == 1:
			return

		if not self.settings.settings["Always show key overlay"]:
			return

		if self.holding or (self.frame_index < len(self.frames) - 1 and self.oldclick):
			self.frame_index += 1
			if self.frame_index >= len(self.frames):
				self.frame_index -= 1

		elif self.frame_index >= len(self.frames) - 1:
			self.oldclick = False

		if not self.oldclick:
			self.frame_index -= 1
			if self.frame_index < 0:
				self.frame_index += 1

		self.holding = False
		super().add_to_frame(background, x_offset, y_offset, alpha)
		self.scoreentry.add_to_frame(background, x_offset, y_offset, self.n,
		                             self.frame_index)


class InputOverlayBG(FrameObject):
	def add_to_frame(self, background, x_offset, y_offset):
		if not self.settings.settings["Always show key overlay"]:
			return

		# special y_offset
		y_offset = y_offset + self.frames[0].size[1]//2
		super().add_to_frame(background, x_offset, y_offset)
