from ImageProcess.Objects.FrameObject import FrameObject


class Cursor(FrameObject):
	pass


class Cursortrail(FrameObject):
	# todo: cursormiddle
	def __init__(self, trail_frames,):
		super().__init__(trail_frames)
		self.trail = [[0, 0]] * 8

	def set_cursor(self, cursor_x, cursor_y):
		self.trail = [[cursor_x, cursor_y] for _ in range(8)]

	def add_to_frame(self, background, x_offset, y_offset, alpha=1):
		# snake algorithm, previous takes the next's one place, etc... the first one takes (x_offset, y_offset) pos.
		self.trail[-1][0], self.trail[-1][1] = x_offset, y_offset
		for x in range(len(self.trail) - 1):
			self.trail[x][0], self.trail[x][1] = self.trail[x + 1][0], self.trail[x + 1][1]
			self.frame_index = x
			super().add_to_frame(background, self.trail[x][0], self.trail[x][1])

