from Objects.abstracts import *


class Cursor(Images):
	def __init__(self, filename, scale):
		Images.__init__(self, filename, scale * 0.75)


class Cursortrail(Images):
	# todo: cursormiddle
	def __init__(self, filename, cursor_x, cursor_y, scale):
		Images.__init__(self, filename, scale * 0.75)
		self.trail = [[cursor_x, cursor_y] for _ in range(8)]
		self.trail_frames = []
		self.prepare_trails()

	def prepare_trails(self):
		for x in [0.45, 0.5, 0.6, 0.65, 0.75, 0.9, 1, 0]:
			buf = super().edit_channel(3, x, new_dst=True)
			img = ImageBuffer(buf, *self.buf.shape())
			self.trail_frames.append(img)

	def add_to_frame(self, background, x_offset, y_offset):
		# snake algorithm, previous takes the next's one place, etc... the first one takes (x_offset, y_offset) pos.
		self.trail[-1][0], self.trail[-1][1] = x_offset, y_offset
		for x in range(len(self.trail) - 1):
			self.trail[x][0], self.trail[x][1] = self.trail[x + 1][0], self.trail[x + 1][1]
			self.img = self.trail_frames[x]
			super().add_to_frame(background, self.trail[x][0], self.trail[x][1])
