import os
import numpy as np
from PIL import Image
from ImageProcess import imageproc

FORMAT = ".png"


class YImage:
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

	def tosquare(self):
		"""
		When the image needs rotation, it will be cropped. So we make the image box bigger.
		"""
		dim = int(np.sqrt(self.img.size[0]**2 + self.img.size[1]**2))
		square = Image.new("RGBA", (dim, dim))
		square.paste(self.img, ((dim - self.img.size[0])//2, (dim - self.img.size[1])//2))
		self.img = square

	def changealpha(self, alpha):
		imageproc.changealpha(self.img, alpha)

	def change_size(self, scale_row, scale_col):
		"""
		When using this method, the original image size will be used
		:param scale_row: float
		:param scale_col: float
		:return:
		"""
		self.img = imageproc.change_size(self.img, scale_row, scale_col, rows=self.orig_rows, cols=self.orig_cols)


class YImages:
	def __init__(self, path, filename, scale, delimiter="", rotate=0):
		self.path = path
		self.filename = filename
		self.scale = scale
		self.delimiter = delimiter
		self.frames = []

		counter = 0
		should_continue = os.path.isfile(self.path + self.filename + self.delimiter + str(0) + ".png")
		while should_continue:
			img = YImage(self.path + self.filename + self.delimiter + str(counter), self.scale, rotate)
			self.frames.append(img.img)
			counter += 1
			should_continue = os.path.isfile(self.path + self.filename + self.delimiter + str(counter) + ".png")
		if not self.frames:
			a = YImage(self.path + self.filename, self.scale, rotate)
			self.frames.append(a.img)

		self.n_frame = len(self.frames)

class ACircle(YImage):
	def __init__(self, filename):
		YImage.__init__(self, filename)
