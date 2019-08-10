from Objects.abstracts import *


class URBar(Images):
	def __init__(self, scale, scorewindow, width, height, simulate=False):
		self.simulate = simulate
		self.scale = scale
		self.w, self.h = int(200 * scale), int(25 * scale)
		self.y = height - self.h//2
		self.x = width//2
		self.barheight = int(self.h/5)
		self.divide_by_255 = 1 / 255.0

		self.colors = [(50, 210, 255, 255), (50, 255, 80, 255), (255, 205, 60, 255)]

		self.maxtime = scorewindow[2]
		self.widths = [int(self.w),
		               int(scorewindow[1]/self.maxtime * self.w),
		               int(scorewindow[0]/self.maxtime * self.w)]
		self.xstart = [0, (self.w - self.widths[1])//2, (self.w - self.widths[2])//2]

		self.bars = []
		self.resultdict = {50: 0, 100: 1, 300: 2}

		self.bar_images = []
		self.prepare_bar()

	def to_3channel(self, image):
		# convert 4 channel to 3 channel, so we can ignore alpha channel, this will optimize the time of add_to_frame
		# where we needed to do each time alpha_s * img[:, :, 0:3]. Now we don't need to do it anymore
		alpha_s = image[:, :, 3] * self.divide_by_255
		for c in range(3):
			image[:, :, c] = image[:, :, c] * alpha_s

	def prepare_bar(self):
		for i in range(3):
			self.bar_images.append(np.zeros((self.h, 4, 4)))
			for c in range(3):
				self.bar_images[-1][:, :, c] = self.colors[i][c]
				self.bar_images[-1][self.barheight * 2:self.barheight * 3, :, c] += 50
			self.bar_images[-1][:, :, :][self.bar_images[-1][:, :, :] > 255] = 255
			self.bar_images[-1][:, :, 3] = 150
			self.bar_images[-1][self.barheight * 2:self.h - self.barheight * 2, :, 3] = 255
			self.to_3channel(self.bar_images[-1])

	def add_bar(self, delta_t, hitresult):
		pos = int(self.w/2 + delta_t/self.maxtime * self.w/2)
		self.bars.append([pos, 1, self.resultdict[hitresult]])

	def add_to_frame(self, background):
		blank = np.zeros((self.h, self.w, 4), np.uint8)
		blank[:, :, 3] = 255
		for i in range(len(self.xstart)):
			cv2.rectangle(blank, (self.xstart[i], self.barheight * 2), (self.xstart[i] + self.widths[i], self.barheight * 3), self.colors[i], -1, cv2.LINE_AA)

		i = len(self.bars)
		while i > 0:
			i -= 1
			bar = self.bars[i]
			self.img = self.bar_images[bar[2]][:, :, :] * bar[1]
			super().add_to_frame(blank, bar[0], self.h//2, 4)
			bar[1] -= 0.0025
			if bar[1] <= 0:
				del self.bars[i]
				break
		if self.simulate:
			return

		cv2.rectangle(blank, (self.w // 2 - 1, 0), (self.w // 2 + 1, self.h), (255, 255, 255, 255), -1, cv2.LINE_AA)
		self.orig_img = blank
		super().to_3channel()
		super().add_to_frame(background, self.x, self.y)
