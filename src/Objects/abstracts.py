import numpy as np
import cv2
import sys

np.set_printoptions(threshold=sys.maxsize)


class Images:
	def __init__(self, filename):
		self.filename = filename
		self.img = cv2.imread(self.filename, -1)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]
		self.change_size(1, 1) # make rows and cols even amount
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]

	def to_3channel(self):
		alpha_s = self.orig_img[:, :, 3] / 255.0
		for c in range(3):
			self.orig_img[:, :, c] = (self.orig_img[:, :, c] * alpha_s).astype(self.orig_img.dtype)
		self.img = np.copy(self.orig_img)

	# crop everything that goes outside the screen
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
		# need to do to_3channel first.
		y1, y2 = y_offset - int(self.img.shape[0] / 2), y_offset + int(self.img.shape[0] / 2)
		x1, x2 = x_offset - int(self.img.shape[1] / 2), x_offset + int(self.img.shape[1] / 2)

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])
		alpha_s = self.img[ystart:yend, xstart:xend, 3] / 255.0
		alpha_l = 1.0 - alpha_s
		for c in range(channel):
			background[y1:y2, x1:x2, c] = (
					self.img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])

	def change_size(self, new_row, new_col, inter_type=cv2.INTER_AREA):
		n_rows = int(new_row * self.orig_rows)
		n_rows -= int(n_rows % 2 == 1)  # need to be even
		n_cols = int(new_col * self.orig_cols)
		n_cols -= int(n_cols % 2 == 1)  # need to be even
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
