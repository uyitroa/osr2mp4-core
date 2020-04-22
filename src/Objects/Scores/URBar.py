from Objects.abstracts import *


class URBar(Images):
	def __init__(self, scale, scorewindow, width, height):
		self.scale = scale
		self.w, self.h = int(200 * scale), int(25 * scale)
		self.y = height - self.h//2
		self.x = width//2
		self.x_offset = self.x - self.w // 2
		self.barheight = int(self.h/5)

		self.colors = [(255, 210, 50, 150), (80, 255, 50, 150), (60, 205, 255, 150)]

		self.maxtime = scorewindow[2]
		self.widths = [int(self.w),
		               int(scorewindow[1]/self.maxtime * self.w),
		               int(scorewindow[0]/self.maxtime * self.w)]
		self.xstart = [0, (self.w - self.widths[1])//2, (self.w - self.widths[2])//2]
		self.bars = []
		self.resultdict = {50: 0, 100: 1, 300: 2}

		self.bar_images = []
		self.prepare_bar()

	def prepare_bar(self):
		for i in range(3):
			self.bar_images.append(Image.new("RGBA", (4, self.h), self.colors[i]))

		self.urbar = Image.new("RGBA", (self.w, self.h))
		for i in range(len(self.xstart)):
			self.urbar.paste(self.colors[i], (self.xstart[i], self.barheight * 2, self.xstart[i] + self.widths[i], self.barheight * 3))

	def add_bar(self, delta_t, hitresult):
		pos = int(self.w/2 + delta_t/self.maxtime * self.w/2)
		self.bars.append([pos, 200, self.resultdict[hitresult]])

	def add_to_frame_bar(self, background):
		self.img = self.urbar
		super().add_to_frame(background, self.x, self.y)
		self.img = Image.new("RGBA", (4, self.h), (255, 255, 255, 255))
		super().add_to_frame(background, self.x, self.y)

	def determine(self, i):
		background = self.bg
		bar = self.bars[i]
		self.img = self.bar_images[bar[2]]
		super().add_to_frame(background, self.x_offset + bar[0], self.y, alpha=bar[1]/200)
		bar[1] -= 1
		if bar[1] <= 0:
			return False
		return True

	def add_to_frame(self, background):
		self.bg = background
		self.bars = [self.bars[i] for i in range(len(self.bars)) if self.determine(i)]
		#
		# cv2.rectangle(blank, (self.w // 2 - 1, 0), (self.w // 2 + 1, self.h), (255, 255, 255, 255), -1, cv2.LINE_AA)
		# self.orig_img = blank
		# self.img = self.urbar
		# super().add_to_frame(background, self.x, self.y)
