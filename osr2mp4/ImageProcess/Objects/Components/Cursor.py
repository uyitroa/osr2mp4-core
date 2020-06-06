import math
from math import copysign

from PIL import Image

from ... import imageproc
from ..FrameObject import FrameObject


class Cursor(FrameObject):
	pass


class Cursortrail(FrameObject):
	# todo: cursormiddle
	def __init__(self, trail_frames, continuous, settings):
		super().__init__(trail_frames, settings=settings)
		self.continuous = continuous
		self.radius = self.settings.scale * 3
		self.alphas = []  # for continuous trail
		self.updatetime = self.settings.timeframe/self.settings.fps/2
		self.oldtime = 0
		if self.continuous:
			self.frame_index = len(self.frames) - 2
			self.trail = (0, 0)
			self.blank = Image.new("RGBA", (self.settings.width, self.settings.height))
		else:
			self.trail = [[0, 0]] * len(self.frames)
		self.timer = 0
		self.timer2 = 0

	def set_cursor(self, cursor_x, cursor_y, cursor_time):
		if self.continuous:
			return
		self.trail = [[cursor_x, cursor_y] for _ in range(len(self.frames))]
		self.oldtime = cursor_time

	def add_to_frame(self, background, x_offset, y_offset, cursor_time, alpha=1):
		# snake algorithm, previous takes the next's one place, etc... the first one takes (x_offset, y_offset) pos.
		if not self.continuous:
			deltat = cursor_time - self.oldtime
			if deltat < self.updatetime:
				update = False
			else:
				update = True
				self.oldtime = cursor_time
				self.trail[-1][0], self.trail[-1][1] = x_offset, y_offset

			for x in range(len(self.trail) - 1):
				self.trail[x][0], self.trail[x][1] = self.trail[x + 1][0], self.trail[x + 1][1]
				self.frame_index = x
				super().add_to_frame(background, self.trail[x][0], self.trail[x][1])
		else:
			if not self.trail:
				self.trail = (x_offset, y_offset)

			# a = time.time()

			deltax = x_offset - self.trail[0]
			deltay = y_offset - self.trail[1]

			delta = math.sqrt(deltax**2 + deltay**2)
			n_cursor = delta/self.radius

			stepx, stepy = 0, 0
			if n_cursor > 0:
				stepx = abs(deltax/n_cursor)
				xx = self.radius**2 - stepx**2

				# stepy = abs(deltay//n_cursor)
				# yy = self.radius**2 - stepy**2
				# if xx >= 0:
				stepy = math.sqrt(xx)
				# elif yy >= 0:
				# 	stepx = math.sqrt(yy)
				# else:
				# 	stepx = 0
				# 	stepy = 0

			else:
				#imageproc.add(self.frames[self.frame_index], self.blank, x_offset, y_offset)
				pass

			count = 0

			x, y = self.trail
			while count < int(n_cursor):
				# print(nx, ny, x, y, x_offset, y_offset, deltax, deltay)
				x += copysign(stepx, deltax)
				y += copysign(stepy, deltay)
				count += 1
				imageproc.add(self.frames[self.frame_index], self.blank, int(x), int(y), channel=4)
			# print(x, y)
			# count = 0
			# x = self.trail[0]
			# y = self.trail[1]
			# while count < n:
			# 	# print(x, y, x_offset, y_offset, nx, ny)
			# 	x += copysign(stepx, deltax)
			# 	y += copysign(stepy, deltay)
			# 	count += 1
			#
			# 	imageproc.add(self.frames[self.frame_index], self.blank, int(x), int(y))

			self.trail = (x, y)
			imageproc.add(self.blank, background, self.settings.width//2, self.settings.height//2)
			imageproc.changealpha(self.blank, 0.92)
