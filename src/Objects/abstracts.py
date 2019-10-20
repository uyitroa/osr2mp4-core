import os
import numpy as np
import cv2
import pyopencl as cl
#
# np.set_printoptions(threshold=sys.maxsize)


FORMAT = ".png"

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

kernel_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kernels/')

kernel_files = os.listdir(kernel_path)
all_kernel = ""
for file in kernel_files:
	if ".cl" in file:
		all_kernel += open(kernel_path + file).read() + "\n"

prg = cl.Program(ctx, all_kernel).build()


class ImageBuffer:
	def __init__(self, img=None, w=None, h=None, pix=None):
		self.set(img, w, h, pix)

	def shape(self):
		return self.w, self.h, self.pix

	def set(self, img, w, h, pix):
		self.h = None if h is None else np.int32(h)
		self.pix = None if pix is None else np.int32(pix)
		self.w = None if w is None else np.int32(w)
		self.img = img

	def set_shape(self, w, h, pix):
		self.set(self.img, w, h, pix)

	def nbytes(self):
		return self.w * self.h * self.pix


class Images:
	mf = cl.mem_flags
	prg, queue, ctx = prg, queue, ctx

	def __init__(self, filename, scale=1, rotate=0):
		# TODO: remove self from img_np to save memory
		self.filename = filename
		self.img_np = cv2.imread(self.filename + FORMAT, -1)

		if self.img_np is None or self.img_np.shape[0] == 1 or self.img_np.shape[1] == 1:
			print(filename, "exists:", self.img_np is not None)
			self.img_np = np.zeros((2, 2, 4))
		if self.img_np.dtype != np.uint8:
			cv2.normalize(self.img_np, self.img_np, 0, 255, cv2.NORM_MINMAX)
			self.img_np = self.img_np.astype(np.uint8)
			print(self.img_np.dtype, self.filename)
		if rotate:
			self.to_square()

		img = cl.Buffer(self.ctx, self.mf.READ_WRITE | self.mf.COPY_HOST_PTR, hostbuf=self.img_np)
		h, w, pix = self.img_np.shape
		h, w, pix = np.int32(h), np.int32(w), np.int32(pix)
		self.buf = ImageBuffer(img, w, h, pix)
		self.buf.set(*self.change_size(scale, scale))

	def add_color(self, color, buf=None, new_dst=False):
		if buf is None:
			buf = self.buf
		if new_dst:
			dest = cl.Buffer(self.ctx, self.mf.READ_WRITE, buf.nbytes())
		else:
			dest = buf.img
		red, green, blue = np.int32(color[0]), np.int32(color[1]), np.int32(color[2])
		self.prg.add_color(self.queue, (buf.h, buf.w), None, buf.img, dest, buf.w, buf.pix, blue, green, red)

		if new_dst:
			return dest

	def edit_channel(self, c, scale, buf=None, new_dst=False):
		if buf is None:
			buf = self.buf
		if new_dst:
			dest = self.copy_img(buf)
		else:
			dest = buf.img

		self.prg.edit_channel(self.queue, (buf.h, buf.w), None, buf.img, dest, buf.w, buf.pix, np.int32(c), np.float32(scale))

		if new_dst:
			return dest

	def to_square(self):
		max_length = int(np.sqrt(self.img_np.shape[0] ** 2 + self.img_np.shape[1] ** 2) + 2)  # round but with int
		square = np.zeros((max_length, max_length, 4))
		y1, y2 = int(max_length / 2 - self.img_np.shape[0] / 2), int(max_length / 2 + self.img_np.shape[0] / 2)
		x1, x2 = int(max_length / 2 - self.img_np.shape[1] / 2), int(max_length / 2 + self.img_np.shape[1] / 2)
		square[y1:y2, x1:x2, :] = self.img_np[:, :, :]
		self.img_np = square

	def change_size(self, row_scale, col_scale, buf=None):
		if buf is None:
			buf = self.buf

		n_rows = np.int32(max(2, int(row_scale * buf.w)))
		n_rows += np.int32(n_rows % 2 == 1)  # need to be even
		n_cols = np.int32(max(2, int(col_scale * buf.h)))
		n_cols += np.int32(n_cols % 2 == 1)  # need to be even

		dest = cl.Buffer(self.ctx, self.mf.READ_WRITE, n_rows * n_cols * buf.pix)

		self.prg.resize(self.queue, (n_cols, n_rows), None, buf.img, dest, buf.w, buf.h, buf.pix, n_rows, n_cols)

		return dest, n_rows, n_cols, buf.pix

	def rotate_image(self, angle, buf=None):
		if buf is None:
			buf = self.buf
		dest = cl.Buffer(self.ctx, self.mf.READ_WRITE, buf.nbytes())
		cos, sin = np.cos(angle, dtype=np.float32), np.sin(angle, dtype=np.float32)
		self.prg.rotate_img(self.queue, (buf.h, buf.w), None, buf.img, dest, buf.w, buf.h, buf.pix, cos, sin)
		return dest

	# crop everything that goes outside the screen
	@staticmethod
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
		return np.int32(pos1), np.int32(pos2), np.int32(start), np.int32(end)

	def copy_img(self, buf=None):
		if buf is None:
			buf = self.buf

		copy_img = cl.Buffer(self.ctx, self.mf.READ_WRITE, buf.nbytes())
		self.prg.copy(self.queue, (buf.h, buf.w, buf.pix), None, buf.img, copy_img, buf.w, buf.w, buf.pix, np.int32(0), np.int32(0))
		return copy_img

	def overlap(self, buf=None, scalar=None, img2=None, x1=None, x2=None, y1=None, y2=None):

		if x2 == 0 or y2 == 0:
			return

		if buf is None:
			buf = self.buf
		
		x1 = x1 or 0
		if x2 is None:
			x2 = buf.w
		y1 = y1 or 0
		if y2 is None:
			y2 = buf.h

		print(x1, x2, y1, y2)

		if scalar:
			r, g, b, a = np.int32(scalar[0]), np.int32(scalar[1]), np.int32(scalar[2]), np.int32(scalar[3])
			self.prg.overlap_scalar(self.queue, (y2-y1, x2-x1), None, buf.img, buf.w, buf.h, buf.pix, np.int32(x1), np.int32(y1), r, g, b, a)
		elif img2:
			print("\n\nnot yet\n\n")

	def rot90(self, n, buf=None):
		if buf is None:
			buf = self.buf
		funcs = [self.prg.rot90, self.prg.rot180, self.prg.rot270]
		copy_img = cl.Buffer(self.ctx, self.mf.READ_WRITE, buf.nbytes())
		
		n = n % 4

		w, h, pix = buf.shape()
		shape = (w, h, pix) if n % 2 == 0 else (h, w, pix)

		if n == 0:
			return (self.copy_img(buf), *shape)

		funcs[n-1](self.queue, (buf.h, buf.w), None, buf.img, copy_img, w, h, pix)

		return (copy_img, *shape)

	def ensureBGsize(self, bg_buf, overlay_buf):
		if overlay_buf.w > bg_buf.w or overlay_buf.w > bg_buf.h:
			max_height = max(overlay_buf.h, bg_buf.h)
			max_width = max(overlay_buf.w, bg_buf.h)
			new_img = cl.Buffer(self.ctx, self.mf.READ_WRITE, max_height * max_width * bg_buf.pix)
			y = np.int32(max_height/2 - bg_buf.h/2)
			x = np.int32(max_width/2 - bg_buf.w/2)
			self.prg.copy(self.queue, (bg_buf.h, bg_buf.w, bg_buf.pix), None, bg_buf.img, new_img, bg_buf.w, max_width, bg_buf.pix, x, y)
			bg_buf.set(new_img, max_width, max_height, bg_buf.pix)

	def add_to_frame(self, bg_buf, x_offset, y_offset, channel=3, alpha=1, buf=None):
		if buf is None:
			buf = self.buf
		y1, y2 = y_offset - buf.h//2, y_offset + buf.h//2
		x1, x2 = x_offset - buf.w//2, x_offset + buf.w//2

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, bg_buf.h)
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, bg_buf.w)

		alpha = min(100, max(0, alpha))

		if channel == 3:
			func = self.prg.add_to_frame3
		elif channel == 4:
			func = self.prg.add_to_frame4
		else:
			print("wait that's illegal")
			return
		func(self.queue, (y2-y1, x2-x1), None, buf.img, bg_buf.img, buf.w, buf.pix, bg_buf.w, bg_buf.pix, x1, y1, xstart, ystart, np.float32(alpha))



class AnimatableImage:
	# TODO: check this class
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

	def buffer_at(self, index):
		return self.frames[index].buf

	def imagebuffer_at(self, index):
		return self.frames[index].buf.img
	
	def image_at(self, index):
		return self.frames[index]

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
			images[x] = ImageBuffer(self.frames[x].rotate_image(angle), *self.frames[x].buf.shape())
		return images

	def add_to_frame(self, background, x_offset, y_offset, channel=3, alpha=1):
		# self.frames[int(self.index)].img[:, :, :] = self.frames[int(self.index)].img[:, :, :] * alpha
		self.frames[int(self.index)].add_to_frame(background, x_offset, y_offset, channel)
