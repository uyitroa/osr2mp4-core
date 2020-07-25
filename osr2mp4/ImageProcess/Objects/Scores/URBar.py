import cv2
import numpy
from PIL import Image

from ..Components.AScorebar import AScorebar
from ... import imageproc
from ..FrameObject import FrameObject


class URBar(AScorebar):
	def __init__(self, frames, settings):
		AScorebar.__init__(self, frames[0], settings=settings)
		self.scale = settings.scale
		self.settings = settings
		self.w, self.h = int(frames[0].size[0]), int(frames[0].size[1])
		self.y = settings.height - self.h//2
		self.x = settings.width//2

		self.x_offset = self.x - self.w // 2

		self.bars = []
		self.resultdict = {50: 0, 100: 1, 300: 2}

		self.c = 0

		self.np = numpy.zeros((self.h, self.w, 4), dtype=numpy.uint8)
		self.np[:, :, 3] = 0
		self.bar_container = Image.frombuffer("RGBA", (self.w, self.h), self.np, 'raw', "RGBA", 0, 1)
		self.bar_container.readonly = False
		self.urbar, self.bar_images, self.maxtime, self.mask = frames

		# (218, 174, 70), (87, 227, 19), (50, 188, 231)

	def add_bar(self, delta_t, hitresult):
		pos = int(self.w/2 + delta_t/self.maxtime * self.w/2)
		# self.bars.append([pos, 1, self.resultdict[hitresult]])
		img = self.bar_images[self.resultdict[hitresult]]
		# imageproc.add(img, self.bar_container, pos, self.bar_container.size[1]//2, channel=4)
		# imageproc.add(self.bar_images[3], self.bar_container, pos, self.bar_container.size[1]//2, channel=4)
		x = pos-img.shape[1]//2
		y = self.np.shape[0]//2-img.shape[0]//2
		a = self.np[y:y+img.shape[0], x:x+img.shape[1], :] + img
		a = a.clip(0, 255)
		self.np[y:y + img.shape[0], x:x + img.shape[1], :] = a
		# self.np[y:y+img.shape[0], x:x + img.shape[1], 3] = 255
		# cv2.imwrite("test.png", self.np)
		# self.bar_container.save("test1.png")
		# cv2.saved

	def add_to_frame_bar(self, background):
		img = self.urbar
		imageproc.add(img, background, self.x, self.y, alpha=min(1, self.alpha*2))

	def add_to_frame(self, background):
		AScorebar.animate(self)
		self.c += 60/self.settings.fps

		s = self.bar_container.size
		self.bar_container.paste((255, 255, 255, 255), (s[0] // 2 - 1, 0, s[0] // 2 + 1, s[1]))
		img = self.bar_container
		imageproc.add(img, background, self.x_offset + self.w//2, self.y, alpha=min(1, self.alpha*2))

		if self.c >= 4:
			# self.np[:, :, :] = self.np[:, :, :] * 0.99
			imageproc.addalpha(self.bar_container, -0.00001)
			a = self.np[:, :, :3] - self.mask
			self.np[:, :, :3] = a.clip(0, 255)
			self.np[:, :, 3] = (self.np[:, :, 3] - (255.0/self.np[:, :, 3].clip(1, 255)) * 0.4).clip(0, 255)
			# print(self.np[0, 0, 0])
			self.c = 0
		# self.bar_container.save("test.png")
