import numpy as np
import cv2
import sys
import numba
# import utils.calculation

#
# np.set_printoptions(threshold=sys.maxsize)


# crop everything that goes outside the screen
@numba.jit(nopython=True)
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


@numba.jit(nopython=True)
def add_to_frame(background, img, x_offset, y_offset, channel=3):
	# need to do to_3channel first.
	y1, y2 = y_offset - int(img.shape[0] / 2), y_offset + int(img.shape[0] / 2)
	x1, x2 = x_offset - int(img.shape[1] / 2), x_offset + int(img.shape[1] / 2)

	y1, y2, ystart, yend = checkOverdisplay(y1, y2, background.shape[0])
	x1, x2, xstart, xend = checkOverdisplay(x1, x2, background.shape[1])
	alpha_s = img[ystart:yend, xstart:xend, 3] * (1/255.0)
	alpha_l = 1.0 - alpha_s

	# if self.img.dtype != np.uint8:
	# 	self.img = self.img.astype(np.uint8)
	#
	# background[y1:y2, x1:x2, :channel] = utils.calculation.add_to_frame(background[y1:y2, x1:x2, :channel],
	#                                                              self.img[ystart:yend, xstart:xend, :],
	#                                                              alpha_l, channel)

	for c in range(channel):
		background[y1:y2, x1:x2, c] = (
				img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])


class Images:
	divide_by_255 = 1 / 255.0

	def __init__(self, filename, scale=1):
		self.filename = filename
		self.img = cv2.imread(self.filename, -1)
		if self.img.dtype != np.uint8:
			cv2.normalize(self.img, self.img, 0, 255, cv2.NORM_MINMAX)
			self.img = np.uint8(self.img)
			print(self.img.dtype, self.filename)
		if self.img is None or self.img.shape[0] == 1 or self.img.shape[1] == 1:
			print(filename, "exists:", self.img is not None)
			self.img = np.zeros((2, 2, 4))
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]
		self.change_size(scale, scale)  # make rows and cols even amount
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]

	def to_3channel(self):
		alpha_s = self.orig_img[:, :, 3] * self.divide_by_255
		for c in range(3):
			self.orig_img[:, :, c] = self.orig_img[:, :, c] * alpha_s
		self.img = np.copy(self.orig_img)

	def ensureBGsize(self, background, overlay_image):
		if overlay_image.shape[0] > background.shape[0] or overlay_image.shape[1] > background.shape[1]:
			max_height = max(overlay_image.shape[0], background.shape[0])
			max_width = max(overlay_image.shape[1], background.shape[1])
			new_img = np.zeros((max_height, max_width, 4), dtype=overlay_image.dtype)
			y1, y2 = int(new_img.shape[0] / 2 - background.shape[0] / 2), int(
				new_img.shape[0] / 2 + background.shape[0] / 2)
			x1, x2 = int(new_img.shape[1] / 2 - background.shape[1] / 2), int(
				new_img.shape[1] / 2 + background.shape[1] / 2)
			new_img[y1:y2, x1:x2, :] = background[:, :, :]
			return new_img
		return background

	def checkOverdisplay(self, pos1, pos2, limit):
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

	def add_to_frame(self, background, x_offset, y_offset, channel=3):
		add_to_frame(background, self.img, x_offset, y_offset, channel)

	def change_size(self, new_row, new_col, inter_type=cv2.INTER_AREA):
		n_rows = max(2, int(new_row * self.orig_rows))
		n_rows += int(n_rows % 2 == 1)  # need to be even
		n_cols = max(2, int(new_col * self.orig_cols))
		n_cols += int(n_cols % 2 == 1)  # need to be even
		self.img = cv2.resize(self.orig_img, (n_cols, n_rows), interpolation=inter_type)


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
