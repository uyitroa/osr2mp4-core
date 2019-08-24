import os

import numpy as np
import cv2
import numba
# import utils.calculation

#
# np.set_printoptions(threshold=sys.maxsize)


FORMAT = ".png"


# crop everything that goes outside the screen
@numba.njit(fastmath=True)
def checkOverdisplay(pos1, pos2, limit):
	start = 0
	end = pos2 - pos1

	if pos1 >= limit:
		return 0, 0, 0, 0
	if pos2 <= 0:
		return 0, 0, 0, 0

	if pos1 < 0:
		start = -pos1
		pos1 = 0
	if pos2 >= limit:
		end -= pos2 - limit
		pos2 = limit
	return pos1, pos2, start, end


@numba.njit(fastmath=True)
def add_to_frame(background, img, x_offset, y_offset, channel=3):
	# need to do to_3channel first.
	y1, y2 = y_offset - int(img.shape[0] / 2), y_offset + int(img.shape[0] / 2)
	x1, x2 = x_offset - int(img.shape[1] / 2), x_offset + int(img.shape[1] / 2)

	y1, y2, ystart, yend = checkOverdisplay(y1, y2, background.shape[0])
	x1, x2, xstart, xend = checkOverdisplay(x1, x2, background.shape[1])
	alpha_s = img[ystart:yend, xstart:xend, 3] * (1/255.0)
	alpha_l = 1.0 - alpha_s

	for c in range(channel):
		background[y1:y2, x1:x2, c] = (
				img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])


class Images:
	divide_by_255 = 1 / 255.0

	def __init__(self, filename, scale=1, rotate=0):
		self.filename = filename
		self.img = cv2.imread(self.filename + FORMAT, -1)

		if self.img is None or self.img.shape[0] == 1 or self.img.shape[1] == 1:
			print(filename, "exists:", self.img is not None)
			self.img = np.zeros((2, 2, 4))
		if self.img.dtype != np.uint8:
			cv2.normalize(self.img, self.img, 0, 255, cv2.NORM_MINMAX)
			self.img = self.img.astype(np.uint8)
			print(self.img.dtype, self.filename)
		if rotate:
			self.to_square()

		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]
		self.change_size(scale, scale)  # make rows and cols even amount
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]


	def to_3channel(self, applytoself=True, img=None):
		if applytoself:
			img = self.orig_img
		alpha_s = img[:, :, 3] * self.divide_by_255
		for c in range(3):
			img[:, :, c] = img[:, :, c] * alpha_s

		if applytoself:
			self.img = np.copy(img)

	def add_color(self, color, applytoself=True, img=None):
		if applytoself:
			img = self.img
		red = color[0]*self.divide_by_255
		green = color[1]*self.divide_by_255
		blue = color[2]*self.divide_by_255
		img[:, :, 0] = np.multiply(img[:, :, 0], blue, casting='unsafe')
		img[:, :, 1] = np.multiply(img[:, :, 1], green, casting='unsafe')
		img[:, :, 2] = np.multiply(img[:, :, 2], red, casting='unsafe')

	def to_square(self):
		max_length = int(np.sqrt(self.img.shape[0] ** 2 + self.img.shape[1] ** 2) + 2)  # round but with int
		square = np.zeros((max_length, max_length, 4))
		y1, y2 = int(max_length / 2 - self.img.shape[0] / 2), int(max_length / 2 + self.img.shape[0] / 2)
		x1, x2 = int(max_length / 2 - self.img.shape[1] / 2), int(max_length / 2 + self.img.shape[1] / 2)
		square[y1:y2, x1:x2, :] = self.img[:, :, :]
		self.img = square

	def change_size(self, new_row, new_col, inter_type=cv2.INTER_AREA, applytoself=True, img=None):
		if applytoself:
			img = self.orig_img
		n_rows = max(2, int(new_row * img.shape[0]))
		n_rows += int(n_rows % 2 == 1)  # need to be even
		n_cols = max(2, int(new_col * img.shape[1]))
		n_cols += int(n_cols % 2 == 1)  # need to be even
		if applytoself:
			self.img = cv2.resize(img, (n_cols, n_rows), interpolation=inter_type)
			# if self.autosave:
			# 	self.save_alphachannel()
			return True
		else:
			img = cv2.resize(img, (n_cols, n_rows), interpolation=inter_type)
			return img

	def rotate_image(self, angle):
		image_center = tuple(np.array(self.img.shape[1::-1]) / 2)
		rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
		result = cv2.warpAffine(self.img, rot_mat, self.img.shape[1::-1], flags=cv2.INTER_LINEAR)
		return result

	# crop everything that goes outside the screen
	def checkOverdisplay(self, pos1, pos2, limit):
		return checkOverdisplay(pos1, pos2, limit)

	def ensureBGsize(self, background, overlay_image):
		if overlay_image.shape[0] > background.shape[0] or overlay_image.shape[1] > background.shape[1]:
			max_height = max(overlay_image.shape[0], background.shape[0])
			max_width = max(overlay_image.shape[1], background.shape[1])
			new_img = np.zeros((max_height, max_width, 4), dtype=overlay_image.dtype)
			y1, y2 = int(new_img.shape[0] / 2 - background.shape[0] / 2), int(new_img.shape[0] / 2 + background.shape[0] / 2)
			x1, x2 = int(new_img.shape[1] / 2 - background.shape[1] / 2), int(new_img.shape[1] / 2 + background.shape[1] / 2)
			new_img[y1:y2, x1:x2, :] = background[:, :, :]
			return new_img
		return background

	def add_to_frame(self, background, x_offset, y_offset, channel=3):
		add_to_frame(background, self.img, x_offset, y_offset, channel)


class AnimatableImage:
	def __init__(self, path, filename, scale, hasframes=False, delimiter="", rotate=0):
		self.path = path
		self.filename = filename
		self.scale = scale
		self.delimiter = delimiter
		self.frames = []
		self.n_frame = 0
		self.index = 0
		if hasframes:
			self.load_frames(rotate)
			self.n_frame = len(self.frames)

	def set_index(self, index):
		self.index = max(0, min(len(self.frames)-1, index))

	def get_index(self):
		return self.index

	def add_index(self, index):
		self.index = max(0, min(len(self.frames) - 1, self.index + index))

	def image_at(self, index):
		return self.frames[index]

	def nparray_at(self, index):
		return self.frames[index].img

	def load_frames(self, rotate):
		counter = 0
		should_continue = os.path.isfile(self.path + self.filename + self.delimiter + str(0) + ".png")
		img = None
		while should_continue:
			self.frames.append(img)
			img = Images(self.path + self.filename + self.delimiter + str(counter), self.scale, rotate)
			img.to_3channel()
			counter += 1
			should_continue = os.path.isfile(self.path + self.filename + self.delimiter + str(counter) + ".png")
		if not self.frames:
			self.frames.append(Images(self.path + self.filename, self.scale, rotate))
		else:
			self.frames.pop(0)

	def prepare_frames(self):
		pass

	def rotate_images(self, angle):
		images = [None] * self.n_frame
		for x in range(self.n_frame):
			images[x] = self.frames[x].rotate_image(angle)
		return images

	def add_to_frame(self, background, x_offset, y_offset, channel=3, alpha=1):
		# self.frames[int(self.index)].img[:, :, :] = self.frames[int(self.index)].img[:, :, :] * alpha
		self.frames[int(self.index)].add_to_frame(background, x_offset, y_offset, channel)


class ACircle(Images):
	def __init__(self, filename, hitcircle_cols, hitcircle_rows):
		Images.__init__(self, filename)
	# if self.orig_cols != hitcircle_cols or self.orig_rows != hitcircle_rows:
	# 	cols_scale = hitcircle_cols/self.orig_cols
	# 	rows_scale = hitcircle_rows/self.orig_rows
	# 	self.change_size(rows_scale, cols_scale, inter_type=cv2.INTER_LINEAR)
	# 	self.orig_cols = hitcircle_cols
	# 	self.orig_rows = hitcircle_rows
	# 	self.orig_img = np.copy(self.img)
	# 	print(filename)
	# print(self.orig_img.shape, self.img.shape, self.orig_cols, self.orig_rows)
