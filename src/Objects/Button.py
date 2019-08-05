from Objects.abstracts import *

scoreentry = "scoreentry-"
inputoverlay = "inputoverlay-key.png"


class ScoreEntry(Images):
	def __init__(self, path, scale, color):
		self.divide_by_255 = 1/255.0
		self.numbers = []
		for x in range(10):
			self.numbers.append(Images(path + scoreentry + str(x) + ".png", scale))
			self.numbers[-1].to_3channel()
		self.prepare_animation(color)

	def add_color(self, image, color):
		red = color[0]*self.divide_by_255
		green = color[1]*self.divide_by_255
		blue = color[2]*self.divide_by_255
		image[:, :, 0] = np.multiply(image[:, :, 0], blue, casting='unsafe')
		image[:, :, 1] = np.multiply(image[:, :, 1], green, casting='unsafe')
		image[:, :, 2] = np.multiply(image[:, :, 2], red, casting='unsafe')
		# image[image > 255] = 255

	def prepare_animation(self, color):
		self.numbers_animation = []
		for img in self.numbers:
			self.numbers_animation.append([])
			tmp = np.copy(img.orig_img)
			self.add_color(img.orig_img, color)
			for size in range(100, 82, -3):
				size /= 100
				img.change_size(size, size)
				self.numbers_animation[-1].append(np.copy(img.img))
			img.orig_img = tmp

	def add_to_frame(self, background, x_offset, y_offset, number, index=0):
		number = str(number)
		x_start = x_offset - int((len(number)-1)/2 * self.numbers_animation[0][index].shape[1])
		for digit in number:
			digit = int(digit)
			self.img = self.numbers_animation[digit][index]
			super().add_to_frame(background, x_start, y_offset)
			x_start += self.img.shape[1]


class InputOverlayFrames(AnimatedImage):
	def __init__(self, path, scale, color):
		AnimatedImage.__init__(self, path, inputoverlay, scale)
		self.color = color
		self.scale = scale
		self.prepare_frames()

	def prepare_frames(self):
		self.frames.append(Images(self.path + inputoverlay, self.scale))
		for size in range(97, 82, -3):
			img = Images(self.path + inputoverlay, self.scale * (size/100))
			img.add_color(self.color)
			img.to_3channel()
			self.frames.append(img)
		self.n_frame = len(self.frames)


class InputOverlay:
	def __init__(self, path, scale, color, scoreentry):
		self.button = InputOverlayFrames(path, scale, color)
		self.scoreentry = scoreentry

		self.holding = False
		self.oldclick = True

		self.button_index = 0

		self.scale = scale
		self.n = 0
		self.color = (0, 0, 0)


	def clicked(self):
		if not self.oldclick:
			self.oldclick = True
			self.n += 1
			self.button_index = 1

		self.holding = True

	def add_to_frame(self, background, x_offset, y_offset):
		if self.holding:
			self.button.add_index(1)

		else:
			self.oldclick = False
			self.button.add_index(-1)

		self.holding = False
		self.button.add_to_frame(background, x_offset, y_offset)
		self.scoreentry.add_to_frame(background, x_offset, y_offset, self.n,
		                             self.button_index)


class InputOverlayBG(Images):
	def __init__(self, filename, scale):
		Images.__init__(self, filename, scale * 1.05)
		self.to_3channel()
		self.orig_img = np.rot90(self.orig_img, 3)
		self.orig_rows = self.orig_img.shape[0]
		self.orig_cols = self.orig_img.shape[1]
		self.img = np.copy(self.orig_img)

	def add_to_frame(self, background, x_offset, y_offset):
		# special y_offset
		y_offset = y_offset + int(self.orig_rows/2)
		super().add_to_frame(background, x_offset, y_offset)
