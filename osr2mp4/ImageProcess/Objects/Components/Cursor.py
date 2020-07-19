import math
from math import copysign

from PIL import Image

from ... import imageproc
from ..FrameObject import FrameObject


class Cursor(FrameObject):
	pass


class Trail:
	def __init__(self, x=0, y=0, timeframe=0):
		self.x = x
		self.y = y
		self.timeframe = timeframe

	def set(self, trail=None, x=None, y=None, timeframe=None):
		if trail is not None:
			self.x, self.y = trail.x, trail.y
			self.timeframe = trail.timeframe
			return
		self.x = x
		self.y = y
		self.timeframe = timeframe


class Cursortrail(FrameObject):
	# todo: cursormiddle
	def __init__(self, trail_frames, continuous, settings):
		super().__init__(trail_frames, settings=settings)
		self.continuous = continuous
		self.radius = self.settings.scale * 3
		self.alphas = []  # for continuous trail
		self.updatetime = 1000/60
		if self.continuous:
			self.frame_index = len(self.frames) - 2
			self.trail = Trail()
			self.blank = Image.new("RGBA", (self.settings.width, self.settings.height))
		else:
			self.trail = [Trail() for _ in range(len(self.frames))]

	def set_cursor(self, cursor_x, cursor_y, cursor_time):
		if self.continuous:
			return
		self.trail = [Trail(x=cursor_x, y=cursor_y, timeframe=cursor_time) for _ in range(len(self.frames))]

	def apply_normaltrail(self, cursor_time, x_offset, y_offset):
		# snake algorithm, previous takes the next's one place, etc... the first one takes (x_offset, y_offset) pos.
		self.trail[-1].set(x=x_offset, y=y_offset, timeframe=cursor_time)

		for x in range(len(self.trail) - 1):
			self.trail[x].set(trail=self.trail[x+1])

	def apply_continuoustrail(self, x_offset, y_offset):
		if not self.trail:
			self.trail = Trail(x=x_offset, y=y_offset)
		deltax = x_offset - self.trail.x
		deltay = y_offset - self.trail.y
		delta = math.sqrt(deltax ** 2 + deltay ** 2)
		n_cursor = delta / self.radius
		stepx, stepy = 0, 0
		if n_cursor > 0:
			stepx = abs(deltax / n_cursor)
			xx = self.radius ** 2 - stepx ** 2
			stepy = math.sqrt(max(0, xx))  # avoid maths domain error temporary fix(?)
		count = 0
		x, y = self.trail.x, self.trail.y
		while count < int(n_cursor):
			x += copysign(stepx, deltax)
			y += copysign(stepy, deltay)
			count += 1
			imageproc.add(self.frames[self.frame_index], self.blank, int(x), int(y), channel=4)
		self.trail.set(x=x, y=y)

	def add_to_frame(self, background, x_offset, y_offset, cursor_time, alpha=1):
		if not self.continuous:
			deltatime = abs(cursor_time - self.trail[-1].timeframe)
			# print(deltatime/self.updatetime)
			for i in range(round(deltatime/self.updatetime - 0.25)):
				self.apply_normaltrail(cursor_time, x_offset, y_offset)
			for i in range(len(self.trail)-1):
				self.frame_index = i
				super().add_to_frame(background, self.trail[i].x, self.trail[i].y)
		else:
			self.apply_continuoustrail(x_offset, y_offset)
			imageproc.add(self.blank, background, self.settings.width // 2, self.settings.height // 2)
			imageproc.changealpha(self.blank, 0.92)
