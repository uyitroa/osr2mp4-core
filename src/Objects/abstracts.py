import os

import numpy as np
import time
from PIL import Image, ImageEnhance

# import utils.calculation

#
# np.set_printoptions(threshold=sys.maxsize)


FORMAT = ".png"


class Timer:
	add_to_frame_timer = 0
	newalpha_timer = 0


class Images:
	def __init__(self, filename, scale=1, rotate=0):
		self.filename = filename
		self.img = Image.open(self.filename + FORMAT).convert("RGBA")
		# if needconversion:
		# 	cv2.normalize(self.img, self.img, 0, 255, cv2.NORM_MINMAX)
		# 	self.img = np.uint8(self.img)
		# 	print(self.img.dtype)
		if rotate:
			self.tosquare()
		if self.img is None or self.img.size[1] == 1 or self.img.size[0] == 1:
			print(filename, "exists:", self.img is not None)
			self.img = Image.new('RGBA', (2, 2))
		self.orig_img = self.img.copy()
		self.orig_rows = self.img.size[1]
		self.orig_cols = self.img.size[0]
		if scale != 1:
			self.change_size(scale, scale) # make rows and cols even amount
			self.orig_img = self.img.copy()
			self.orig_rows = self.img.size[1]
			self.orig_cols = self.img.size[0]

	# def to_3channel(self):
	# 	alpha_s = self.orig_img[:, :, 3] * self.divide_by_255
	# 	for c in range(3):
	# 		self.orig_img[:, :, c] = self.orig_img[:, :, c] * alpha_s
	# 	self.img = np.copy(self.orig_img)

	# crop everything that goes outside the screen
	# def checkOverdisplay(self, pos1, pos2, limit):
	# 	start = 0
	# 	end = pos2 - pos1
	#
	# 	if pos1 >= limit:
	# 		return 0, 0, 0, 0
	# 	if pos2 <= 0:
	# 		return 0, 0, 0, 0
	#
	# 	if pos1 < 0:
	# 		start = -pos1
	# 		pos1 = 0
	# 	if pos2 >= limit:
	# 		end -= pos2 - limit
	# 		pos2 = limit
	# 	return pos1, pos2, start, end

	# def ensureBGsize(self, background, overlay_image):
	# 	if overlay_image.size[1] > background.size[1] or overlay_image.size[0] > background.size[0]:
	# 		max_height = max(overlay_image.size[1], background.size[1])
	# 		max_width = max(overlay_image.size[0], background.size[0])
	# 		new_img = np.zeros((max_height, max_width, 4), dtype=overlay_image.dtype)
	# 		y1, y2 = int(new_img.size[1] / 2 - background.size[1] / 2), int(new_img.size[1] / 2 + background.size[1] / 2)
	# 		x1, x2 = int(new_img.size[0] / 2 - background.size[0] / 2), int(new_img.size[0] / 2 + background.size[0] / 2)
	# 		new_img[y1:y2, x1:x2, :] = background[:, :, :]
	# 		return new_img
	# 	return background

	def tosquare(self):
		dim = int(np.sqrt(self.img.size[0]**2 + self.img.size[1]**2))
		square = Image.new("RGBA", (dim, dim))
		square.paste(self.img, ((dim - self.img.size[0])//2, (dim - self.img.size[1])//2))
		self.img = square

	def changealpha(self, img, opacity):
		alpha = img.split()[3]
		alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
		img.putalpha(alpha)

	def newalpha(self, img, alpha):
		asdf = time.time()
		r, g, b, a = img.split()
		a = a.point(lambda i: i * alpha)
		out = Image.merge('RGBA', (r, g, b, a))
		Timer.newalpha_timer += time.time() - asdf
		return out

	def add_color(self, image, color):
		"""
		:param image:  PIL.Image
		:param color: tuple RGB
		:return: PIL.Image
		"""
		im = image.convert('RGBA')
		r, g, b, a = im.split()
		r = r.point(lambda i: i * color[0] / 255)
		g = g.point(lambda i: i * color[1] / 255)
		b = b.point(lambda i: i * color[2] / 255)
		return Image.merge('RGBA', (r, g, b, a))

	def add_to_frame(self, background, x_offset, y_offset, channel=3):
		asdf = time.time()
		y1 = y_offset - int(self.img.size[1] / 2)
		x1 = x_offset - int(self.img.size[0] / 2)
		#
		# y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.size[1])
		# x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.size[0])
		# alpha_s = self.img[ystart:yend, xstart:xend, 3] * self.divide_by_255
		# alpha_l = 1.0 - alpha_s
		# for c in range(channel):
		# 	background[y1:y2, x1:x2, c] = (
		# 			self.img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])
		background.paste(self.img, (x1, y1), self.img)
		Timer.add_to_frame_timer += time.time() - asdf

	def change_size(self, scale_row, scale_col, img=None):
		if img is None:
			im = self.orig_img
			rows, cols = self.orig_rows, self.orig_cols
		else:
			im = img
			rows = img.size[1]
			cols = img.size[0]
		n_rows = max(2, int(scale_row * rows))
		n_rows += int(n_rows % 2 == 1)  # need to be even
		n_cols = max(2, int(scale_col * cols))
		n_cols += int(n_cols % 2 == 1)  # need to be even
		# self.img = cv2.resize(self.orig_img, (n_cols, n_rows), interpolation=inter_type)
		if img is not None:
			return im.resize((n_cols, n_rows), Image.ANTIALIAS)
		self.img = im.resize((n_cols, n_rows), Image.ANTIALIAS)


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

	def pilimg_at(self, index):
		return self.frames[index].img

	def load_frames(self, rotate):
		counter = 0
		should_continue = os.path.isfile(self.path + self.filename + self.delimiter + str(0) + ".png")
		img = None
		while should_continue:
			self.frames.append(img)
			img = Images(self.path + self.filename + self.delimiter + str(counter), self.scale, rotate)
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
			images[x] = self.frames[x].img.rotate(angle)
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
