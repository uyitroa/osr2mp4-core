import os
import numpy as np
from PIL import Image

from ...EEnum.EImageFrom import ImageFrom
from .. import imageproc


class YImage:
	def __init__(self, filename, settings, scale=1, rotate=0, defaultpath=False, prefix="", fallback=None, scaley=None):
		self.filename = filename
		self.origfile = filename
		self.x2 = False
		self.imgfrom = None

		self.settings = settings

		self.loadimg(defaultpath, prefix, fallback)

		if rotate:
			self.tosquare()

		if scaley is None:
			scaley = scale

		if self.x2:
			# print(self.filename)
			scale /= 2
			scaley /= 2


		self.orig_img = self.img.copy()
		self.orig_rows = self.img.size[1]
		self.orig_cols = self.img.size[0]
		if scale != 1:
			self.change_size(scale, scaley)
			self.orig_img = self.img.copy()
			self.orig_rows = self.img.size[1]
			self.orig_cols = self.img.size[0]

		# print(filename)

	def loadx2(self, path, pre, filename=None):
		if filename is None:
			filename = self.filename
		try:
			self.img = Image.open(path + pre + filename + self.settings.x2 + self.settings.format).convert("RGBA")
			self.filename = path + pre + filename + self.settings.x2 + self.settings.format
			self.x2 = True
			return True
		except FileNotFoundError as er:
			# print(er)
			try:
				self.img = Image.open(path + pre + filename + self.settings.format).convert("RGBA")
				self.filename = path + pre + filename + self.settings.format
				return True
			except FileNotFoundError as e:
				return False

	def loadimg(self, defaultpath, prefix, fallback):
		pre = self.settings.skin_ini.fonts.get(prefix, "")
		default_pre = self.settings.default_skin_ini.fonts.get(prefix, "")

		if defaultpath:
			path = self.settings.default_path
		else:
			path = self.settings.skin_path

		if self.loadx2(path, pre):
			if defaultpath:
				self.imgfrom = ImageFrom.DEFAULT_X2 if self.x2 else ImageFrom.DEFAULT_X
			else:
				self.imgfrom = ImageFrom.SKIN_X2 if self.x2 else ImageFrom.SKIN_X
			return

		if fallback is not None:
			if self.loadx2(path, pre, fallback):
				self.imgfrom = ImageFrom.FALLBACK_X2 if self.x2 else ImageFrom.FALLBACK_X
				return
			self.filename = fallback

		if self.loadx2(self.settings.default_path, default_pre):
			self.imgfrom = ImageFrom.DEFAULT_X2 if self.x2 else ImageFrom.DEFAULT_X
			return

		self.filename = "None"
		self.img = Image.new("RGBA", (1, 1))
		self.imgfrom = ImageFrom.BLANK

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
	def __init__(self, filename, settings, scale, delimiter="", rotate=0):
		self.settings = settings
		self.filename = filename
		self.scale = scale
		self.delimiter = delimiter
		self.frames = []
		self.rotate = rotate
		self.n_frame = 0
		self.unanimate = False
		self.imgfrom = None

		self.load(defaultpath=False)
		if self.n_frame == 0:
			print("Loading default path YImagesss", filename)
			self.load(defaultpath=True)

	def load(self, defaultpath=False):
		counter = 0

		if defaultpath:
			path = self.settings.default_path
		else:
			path = self.settings.skin_path

		should_continue = os.path.isfile(path + self.filename + self.delimiter + str(0) + self.settings.format)
		should_continue = should_continue or os.path.isfile(path + self.filename + self.delimiter + str(0) + self.settings.x2 + self.settings.format)

		while should_continue:

			img = YImage(self.filename + self.delimiter + str(counter), self.settings, scale=self.scale, rotate=self.rotate, defaultpath=defaultpath)
			self.imgfrom = img.imgfrom
			self.frames.append(img.img)

			counter += 1

			should_continue = os.path.isfile(path + self.filename + self.delimiter + str(counter) + self.settings.format)
			should_continue = should_continue or os.path.isfile(path + self.filename + self.delimiter + str(counter) + self.settings.x2 + self.settings.format)


		if not self.frames:
			should_continue = os.path.isfile(path + self.filename + self.settings.format)
			if should_continue:
				self.unanimate = True

				a = YImage(self.filename, self.settings, scale=self.scale, rotate=self.rotate, defaultpath=defaultpath)
				self.imgfrom = a.imgfrom
				self.frames.append(a.img)


		self.n_frame = len(self.frames)

