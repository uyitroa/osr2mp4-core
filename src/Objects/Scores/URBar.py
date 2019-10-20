from Objects.abstracts import *


class URBar:
	def __init__(self, scale, scorewindow, width, height):
		self.scale = scale
		self.w, self.h = int(200 * scale), int(25 * scale)
		self.h += int(self.h % 2 == 1)
		self.w += int(self.w % 2 == 1)

		self.y = height - self.h//2
		self.x = width//2
		self.barheight = int(self.h/5)
		self.divide_by_255 = 1 / 255.0

		self.colors = [(50, 210, 255), (50, 255, 80), (255, 205, 60)]

		self.maxtime = scorewindow[2]
		self.widths = [int(self.w),
		               int(scorewindow[1]/self.maxtime * self.w),
		               int(scorewindow[0]/self.maxtime * self.w)]
		self.xstart = [0, (self.w - self.widths[1])//2, (self.w - self.widths[2])//2]

		self.bars = []
		self.resultdict = {50: 0, 100: 1, 300: 2}

		self.bar_images = []
		self.prepare_bar()

	# def to_3channel(self, image):
	# 	# convert 4 channel to 3 channel, so we can ignore alpha channel, this will optimize the time of add_to_frame
	# 	# where we needed to do each time alpha_s * img[:, :, 0:3]. Now we don't need to do it anymore
	# 	alpha_s = image[:, :, 3] * self.divide_by_255
	# 	for c in range(3):
	# 		image[:, :, c] = image[:, :, c] * alpha_s

	def prepare_bar(self):
		for i in range(3):
			self.bar_images.append(np.zeros((self.h, 4, 3)))
			for c in range(3):
				self.bar_images[-1][:, :, c] = self.colors[i][c]
			# self.bar_images[-1][:, :, :][self.bar_images[-1][:, :, :] > 255] = 255

	def add_bar(self, delta_t, hitresult):
		pos = int(self.w/2 + delta_t/self.maxtime * self.w/2)
		self.bars.append([pos, 1, self.resultdict[hitresult]])

	# @staticmethod
	# def checkOverdisplay(pos1, pos2, limit):
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

	def overlay_bar(self, background, img, x_offset, y_offset, alpha=1):
		# need to do to_3channel first.
		y1, y2 = y_offset - int(img.shape[0] / 2), y_offset + int(img.shape[0] / 2)
		x1, x2 = x_offset - int(img.shape[1] / 2), x_offset + int(img.shape[1] / 2)

		mask = background[y1:y2, x1:x2, :] + img[:, :, :] * alpha
		mask[mask > 255] = 255
		background[y1:y2, x1:x2, :] = mask

	def overlay(self, background, img, x_offset, y_offset):
		y1, y2 = y_offset - int(img.shape[0] / 2), y_offset + int(img.shape[0] / 2)
		x1, x2 = x_offset - int(img.shape[1] / 2), x_offset + int(img.shape[1] / 2)
		background[y1:y2, x1:x2, :] = img[:, :, :]

	def add_to_frame(self, background):
		blank = np.zeros((self.h, self.w, 3), np.uint8)
		for i in range(len(self.xstart)):
			cv2.rectangle(blank, (self.xstart[i], self.barheight * 2), (self.xstart[i] + self.widths[i], self.barheight * 3), self.colors[i], -1, cv2.LINE_AA)

		i = len(self.bars)
		while i > 0:
			i -= 1
			bar = self.bars[i]
			self.overlay_bar(blank, self.bar_images[bar[2]], bar[0], self.h//2, bar[1])
			bar[1] -= 0.0035
			if bar[1] <= 0:
				del self.bars[i]

		cv2.rectangle(blank, (self.w // 2 - 1, 0), (self.w // 2 + 1, self.h), (255, 255, 255, 255), -1, cv2.LINE_AA)
		self.overlay(background, blank, self.x, self.y)
