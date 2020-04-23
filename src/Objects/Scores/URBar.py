from Objects.abstracts import *


class URBar(Images):
	def __init__(self, scale, scorewindow, width, height):
		self.scale = scale
		self.w, self.h = int(200 * scale), int(25 * scale)
		self.y = height - self.h//2
		self.x = width//2
		self.x_offset = self.x - self.w // 2
		self.barheight = int(self.h/5)

		self.colors = [(255, 200, 77, 175), (89, 255, 9, 175), (44, 186, 255, 175)]

		self.maxtime = scorewindow[2]
		self.widths = [int(self.w),
		               int(scorewindow[1]/self.maxtime * self.w),
		               int(scorewindow[0]/self.maxtime * self.w)]
		self.xstart = [0, (self.w - self.widths[1])//2, (self.w - self.widths[2])//2]
		self.bars = []
		self.resultdict = {50: 0, 100: 1, 300: 2}

		self.bar_images = []
		self.timer = 0
		self.prepare_bar()

	def prepare_bar(self):
		for i in range(3):
			self.bar_images.append(Image.new("RGBA", (4, self.h), self.colors[i]))
		self.bar_container = Image.new("RGBA", (self.w, self.h))

		self.urbar = Image.new("RGBA", (self.w, self.h))
		for i in range(len(self.xstart)):
			self.urbar.paste(self.colors[i], (self.xstart[i], self.barheight * 2, self.xstart[i] + self.widths[i], self.barheight * 3))

	def add_bar(self, delta_t, hitresult):
		asdf = time.time()
		pos = int(self.w/2 + delta_t/self.maxtime * self.w/2)
		# self.bars.append([pos, 1, self.resultdict[hitresult]])
		self.img = self.bar_images[self.resultdict[hitresult]]
		super().add_to_frame(self.bar_container, pos, self.bar_container.size[1]//2)
		s = self.bar_container.size
		self.bar_container.paste((255, 255, 255, 255), (s[0]//2 - 1, 0, s[0]//2 + 1, s[1]))
		self.timer += time.time() - asdf


	def add_to_frame(self, background):
		self.bg = background
		self.img = self.bar_container
		super().add_to_frame(background, self.x_offset + self.w//2, self.y)
		super().changealpha(self.bar_container, 0.999)
		#
		# cv2.rectangle(blank, (self.w // 2 - 1, 0), (self.w // 2 + 1, self.h), (255, 255, 255, 255), -1, cv2.LINE_AA)
		# self.orig_img = blank
		# self.img = self.urbar
		# super().add_to_frame(background, self.x, self.y)
