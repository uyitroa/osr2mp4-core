from math import ceil

from ... import imageproc
from ..FrameObject import FrameObject


class ComboCounter(FrameObject):
	def __init__(self, frames, gap, settings):
		self.settings = settings

		self.score_frames, self.score_fadeout = frames
		self.height = self.settings.height
		self.width = self.settings.width

		self.score_index = 0
		self.index_step = 1
		self.fadeout_index = 0

		self.combofadeout = 0
		self.combo = 0
		self.breaking = False
		self.adding = False
		self.animate = False

		self.gap = int(gap * self.settings.scale)

	def breakcombo(self):
		self.breaking = True
		self.adding = False
		self.animate = False
		self.combofadeout = 0

	def add_combo(self, combo=None):
		if self.breaking:
			self.combo = 0
		if self.adding:
			self.combo = self.combofadeout
			self.score_index = 0
			self.index_step = 1
			self.animate = True

		self.breaking = False
		self.adding = True

		self.fadeout_index = 0
		if combo is None:
			self.combofadeout += 1
		else:
			self.combofadeout = combo

	def get_combo(self):
		return max(0, self.combofadeout-1)

	def set_combo(self, combo):
		self.combofadeout = combo
		self.combo = max(0, combo-1)

	def next_pos(self, x, y, img):
		x += img.size[0] - self.gap
		x_offset = x - img.size[0] // 2
		y_offset = y + img.size[1] // 2
		return x, x_offset, y_offset

	def draw_combo(self, combo, background, frames, index):
		x = 10 * self.settings.scale
		for digit in str(combo):
			digit = int(digit)
			img = frames[digit][int(index)]
			y = self.height - img.size[1]
			x, x_offset, y_offset = self.next_pos(x, y, img)
			imageproc.add(img, background, x_offset, y_offset)

		img = frames[10][int(index)]
		y = self.height - img.size[1]
		x, x_offset, y_offset = self.next_pos(x, y, img)
		imageproc.add(img, background, x_offset, y_offset)

	def add_to_frame(self, background, inbreak):
		if int(self.fadeout_index) == len(self.score_fadeout[0]) - 1:
			self.combo = self.combofadeout
			self.score_index = 0
			self.index_step = 1
			self.fadeout_index = 0
			self.animate = True
			self.adding = False

		if self.breaking:
			self.combo = max(0, self.combo - 1)

		if int(self.score_index) == len(self.score_frames[0]) - 1:
			self.index_step = -1

		if ceil(self.score_index) == 0 and self.animate and self.index_step == -1:
			self.animate = False

		if self.adding:
			if self.settings.settings["In-game interface"] or inbreak:
				self.draw_combo(self.combofadeout, background, self.score_fadeout, self.fadeout_index)

			self.fadeout_index += 1

		if self.settings.settings["In-game interface"] or inbreak:
			self.draw_combo(self.combo, background, self.score_frames, self.score_index)

		if self.animate:
			self.score_index += self.index_step
