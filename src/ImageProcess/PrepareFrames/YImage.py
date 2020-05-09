import os
import numpy as np
from PIL import Image
from ImageProcess import imageproc
from global_var import SkinPaths


class YImage:
	def __init__(self, filename, scale=1, rotate=0, defaultpath=False, prefix="", fallback=None):
		self.filename = filename
		self.origfile = filename
		self.x2 = False

		self.loadimg(defaultpath, prefix, fallback)

		if rotate:
			self.tosquare()

		if self.x2:
			# print(self.filename)
			scale /= 2

		self.orig_img = self.img.copy()
		self.orig_rows = self.img.size[1]
		self.orig_cols = self.img.size[0]
		if scale != 1:
			self.change_size(scale, scale)  # make rows and cols even amount
			self.orig_img = self.img.copy()
			self.orig_rows = self.img.size[1]
			self.orig_cols = self.img.size[0]

		# print(filename)

	def loadx2(self, path, pre, filename=None):
		if filename is None:
			filename = self.filename
		try:
			self.img = Image.open(path + pre + filename + SkinPaths.x2 + SkinPaths.format).convert("RGBA")
			self.filename = path + pre + filename + SkinPaths.x2 + SkinPaths.format
			self.x2 = True
			return True
		except FileNotFoundError as er:
			# print(er)
			try:
				self.img = Image.open(path + pre + filename + SkinPaths.format).convert("RGBA")
				self.filename = path + pre + filename + SkinPaths.format
				return True
			except FileNotFoundError as e:
				return False

	def loadimg(self, defaultpath, prefix, fallback):
		pre = SkinPaths.skin_ini.fonts.get(prefix, "")
		default_pre = SkinPaths.default_skin_ini.fonts.get(prefix, "")

		if defaultpath:
			path = SkinPaths.default_path
		else:
			path = SkinPaths.path

		if self.loadx2(path, pre):
			return

		if fallback is not None:
			if self.loadx2(path, pre, fallback):
				return
			self.filename = fallback

		print("File {} not found\nTrying default skin files {}".format(self.origfile, self.filename))
		print(pre, default_pre)

		if self.loadx2(SkinPaths.default_path, default_pre):
			return

		print("\nDefault file not found creating blank file")
		self.filename = "None"
		self.img = Image.new("RGBA", (1, 1))

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
	def __init__(self, filename, scale, delimiter="", rotate=0):
		self.filename = filename
		self.scale = scale
		self.delimiter = delimiter
		self.frames = []
		self.rotate = rotate
		self.n_frame = 0
		self.unanimate = False

		self.load(defaultpath=False)
		if self.n_frame == 0:
			print("Loading default path YImagesss", filename)
			self.load(defaultpath=True)

	def load(self, defaultpath=False):
		counter = 0

		if defaultpath:
			path = SkinPaths.default_path
		else:
			path = SkinPaths.path

		should_continue = os.path.isfile(path + self.filename + self.delimiter + str(0) + SkinPaths.format)
		while should_continue:

			img = YImage(self.filename + self.delimiter + str(counter), scale=self.scale, rotate=self.rotate, defaultpath=defaultpath)
			self.frames.append(img.img)

			counter += 1

			should_continue = os.path.isfile(path + self.filename + self.delimiter + str(counter) + SkinPaths.format)


		if not self.frames:
			should_continue = os.path.isfile(path + self.filename + SkinPaths.format)
			if should_continue:
				self.unanimate = True

				a = YImage(self.filename, scale=self.scale, rotate=self.rotate, defaultpath=defaultpath)
				self.frames.append(a.img)


		self.n_frame = len(self.frames)

