from Objects.abstracts import *

scoreentry = "scoreentry-"
inputoverlay = "inputoverlay-key"


class ScoreEntry(Images):
	def __init__(self, path, scale, color):
		self.divide_by_255 = 1/255.0
		self.numbers = []
		for x in range(10):
			self.numbers.append(Images(path + scoreentry + str(x), scale))
		self.prepare_animation(color)

	def prepare_animation(self, color):
		self.numbers_animation = []
		for img in self.numbers:
			self.numbers_animation.append([])
			color_number = ImageBuffer(super().add_color(color, buf=img.buf, new_dst=True), *img.buf.shape())
			for size in range(100, 82, -3):
				size /= 100
				buf = ImageBuffer(*super().change_size(size, size, buf=color_number))
				self.numbers_animation[-1].append(buf)

	def add_to_frame(self, background, x_offset, y_offset, number, index=0):
		number = str(number)
		x_start = x_offset - int((len(number)-1)/2 * self.numbers_animation[0][index].w)
		for digit in number:
			digit = int(digit)
			self.buf = self.numbers_animation[digit][index]
			super().add_to_frame(background, x_start, y_offset)
			x_start += self.buf.w


class InputOverlay(Images):
	def __init__(self, path, scale, color, scoreentry):
		Images.__init__(self, path + inputoverlay, scale)
		self.freeze = 0
		self.scoreentry = scoreentry

		self.holding = False
		self.oldclick = True

		self.button_index = 0

		self.scale = scale
		self.n = 0
		self.color = (0, 0, 0)

		self.button_frames = []

		self.prepare_frames(color)

	def set_freeze(self, freeze, n):
		self.freeze = freeze
		self.n = n

	def prepare_frames(self, color):
		self.button_frames.append(self.buf)
		for size in range(97, 82, -3):
			size /= 100
			buf = ImageBuffer(*self.change_size(size, size))
			self.add_color(color, buf=buf)
			self.button_frames.append(buf)

	def clicked(self, cur_time):
		if not self.oldclick:
			self.oldclick = True
			if cur_time >= self.freeze:
				self.n += 1
			self.button_index = 1

		self.holding = True

	def add_to_frame(self, background, x_offset, y_offset):
		if self.holding:
			self.button_index += 1
			if self.button_index >= len(self.button_frames):
				self.button_index -= 1

		else:
			self.oldclick = False
			self.button_index -= 1
			if self.button_index < 0:
				self.button_index += 1

		self.holding = False
		self.buf = self.button_frames[self.button_index]
		super().add_to_frame(background, x_offset, y_offset)
		self.scoreentry.add_to_frame(background, x_offset, y_offset, self.n,
		                             self.button_index)


class InputOverlayBG(Images):
	def __init__(self, filename, scale):
		Images.__init__(self, filename, scale * 1.05)
		self.buf.set(*super().rot90(3))

	def add_to_frame(self, background, x_offset, y_offset):
		# special y_offset
		y_offset = y_offset + int(self.buf.w/2)
		super().add_to_frame(background, x_offset, y_offset)
