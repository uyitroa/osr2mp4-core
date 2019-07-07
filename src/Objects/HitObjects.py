from Objects.abstracts import *


class HitCircleNumber(Images):
	def __init__(self, filename, circle_radius, default_circle_size):
		Images.__init__(self, filename)
		self.scale = circle_radius * 2 / default_circle_size
		self.change_size(self.scale, self.scale)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]
		self.to_3channel()


class Number:
	def __init__(self, radius, path, default_circle_size):
		self.combo_number = []
		for x in range(10):
			self.combo_number.append(HitCircleNumber(path + "default-" + str(x) + ".png", radius, default_circle_size))

	def draw(self, circle, number, gap):
		"""
		:param circle: array of image circle
		:param number: number
		:param gap: distance between two digits
		"""
		number = str(number)
		size = gap * (len(number) - 1)  # image number size doesn't count because we are going to overlap them.
		x_pos = int((circle.shape[1] / 2) - (size / 2))
		y_pos = int(circle.shape[0] / 2)

		for digit in number:
			self.combo_number[int(digit)].add_to_frame(circle, x_pos, y_pos, 4)
			x_pos += gap


class ApproachCircle(Images):
	def __init__(self, filename, scale, cs, time_preempt, interval, opacity_interval):
		Images.__init__(self, filename)
		self.scale = scale
		self.cs = cs
		self.time_preempt = round(time_preempt)
		self.interval = round(interval)
		self.opacity_interval = opacity_interval
		self.approach_frames = []
		self.prepare_sizes()

	def prepare_sizes(self):
		alpha = 0
		for time_left in range(self.time_preempt, 0, -self.interval):
			alpha = min(100, alpha + self.opacity_interval)
			approach_size = self.cs + (time_left / self.time_preempt) * self.scale * self.cs
			scale = approach_size * 2 / self.orig_cols
			self.change_size(scale, scale)
			self.approach_frames.append(self.img)

	def add_to_frame(self, background, x_offset, y_offset, time_left):
		self.img = self.approach_frames[int((self.time_preempt - time_left) / self.interval)]
		super().add_to_frame(background, x_offset, y_offset)


class CircleOverlay(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)


class SliderCircleOverlay(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)


class CircleSlider(Images):
	def __init__(self, filename, radius_scale):
		Images.__init__(self, filename)


class Circles(Images):
	def __init__(self, filename, overlay_filename, slideroverlay_filename, slidercircle_filename, slider_combo,
	             path, diff, scale, approachfile, maxcombo, gap, colors):
		"""
		:param filename: str hitcircle file
		:param overlay_filename: str circle overlay file
		:param slidercircle_filename: str slidercircle file name
		:param path: str where is the skin folder
		:param diff: dict, contains ApproachRate, CircleSize, OverallDifficulty, HPDrain
		:param scale: float scale of current screen res with 512x384
		:param approachfile: str approach circle file
		:param maxcombo: dict, biggest number we need to overlap, for preparing_circle, where we overlap every number with every circle
		:param gap: int, gap between 2 digits
		"""
		Images.__init__(self, filename)
		self.overlay_filename = overlay_filename
		self.slideroverlay_filename = slideroverlay_filename
		self.diff = diff
		self.circles = []
		self.interval = 1000 / 60  # ms between 2 frames

		self.ar = diff["ApproachRate"]
		self.cs = (54.4 - 4.48 * diff["CircleSize"]) * scale

		self.calculate_ar()
		self.load_circle()

		self.maxcolors = colors["ComboNumber"]
		self.colors = colors
		self.maxcombo = maxcombo
		self.gap = gap

		self.slider_combo = slider_combo
		self.slider_circle = CircleSlider(slidercircle_filename, self.radius_scale)

		self.number_drawer = Number(self.orig_rows / 2, path, self.default_circle_size)
		self.approachCircle = ApproachCircle(approachfile, scale, self.cs, self.time_preempt, self.interval,
		                                     self.opacity_interval)

		self.circle_frames = []
		self.slidercircle_frames = []
		self.prepare_circle()

	def calculate_ar(self):
		if self.ar < 5:
			self.time_preempt = 1200 + 600 * (5 - self.ar) / 5
			self.fade_in = 800 + 400 * (5 - self.ar) / 5
		elif self.ar == 5:
			self.time_preempt = 1200
			self.fade_in = 800
		else:
			self.time_preempt = 1200 - 750 * (self.ar - 5) / 5
			self.fade_in = 800 - 500 * (self.ar - 5) / 5
		self.opacity_interval = int(self.fade_in / 100)

	def add_color(self, image, color):
		red = color[0]/255.0
		green = color[1]/255.0
		blue = color[2]/255.0
		image[:, :, 0] = np.multiply(image[:, :, 0], blue, casting='unsafe')
		image[:, :, 1] = np.multiply(image[:, :, 1], green, casting='unsafe')
		image[:, :, 2] = np.multiply(image[:, :, 2], red, casting='unsafe')
		image[image > 255] = 255

	def load_circle(self):
		self.overlay = CircleOverlay(self.overlay_filename)
		self.slidercircleoverlay = SliderCircleOverlay(self.slideroverlay_filename)
		cur_radius = self.orig_cols / 2
		self.radius_scale = self.cs / cur_radius
		self.default_circle_size = self.orig_rows  # save for number class

	def overlayhitcircle(self, background, x_offset, y_offset, overlay_image):
		# still ned 4 channels so cannot do to_3channel before.
		y1, y2 = y_offset - int(overlay_image.shape[0] / 2), y_offset + int(overlay_image.shape[0] / 2)
		x1, x2 = x_offset - int(overlay_image.shape[1] / 2), x_offset + int(overlay_image.shape[1] / 2)

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])

		alpha_s = overlay_image[ystart:yend, xstart:xend, 3] / 255.0
		alpha_l = 1 - alpha_s
		for c in range(4):
			background[y1:y2, x1:x2, c] = overlay_image[ystart:yend, xstart:xend, c] * alpha_s + \
			                              alpha_l * background[y1:y2, x1:x2, c]

	def overlay_approach(self, background, x_offset, y_offset, circle_img):
		# still ned 4 channels so cannot do to_3channel before.
		y1, y2 = y_offset - int(circle_img.shape[0] / 2), y_offset + int(circle_img.shape[0] / 2)
		x1, x2 = x_offset - int(circle_img.shape[1] / 2), x_offset + int(circle_img.shape[1] / 2)

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])

		alpha_s = background[y1:y2, x1:x2, 3] / 255.0
		alpha_l = 1 - alpha_s
		for c in range(4):
			background[y1:y2, x1:x2, c] = circle_img[ystart:yend, xstart:xend, c] * alpha_l + \
			                              alpha_s * background[y1:y2, x1:x2, c]

	def to_3channel(self, image):
		# convert 4 channel to 3 channel, so we can ignore alpha channel, this will optimize the time of add_to_frame
		# where we needed to do each time alpha_s * img[:, :, 0:3]. Now we don't need to do it anymore
		alpha_s = image[:, :, 3] / 255.0
		for c in range(3):
			image[:, :, c] = (image[:, :, c] * alpha_s).astype(self.orig_img.dtype)

	def prepare_circle(self):
		# prepare every single frame before entering the big loop, this will save us a ton of time since we don't need
		# to overlap number, circle overlay and approach circle every single time.
		for c in range(1, self.maxcolors + 1):
			color = self.colors["Combo" + str(c)]

			self.orig_color_img = np.copy(self.orig_img)
			self.add_color(self.orig_color_img, color)
			self.overlayhitcircle(self.orig_color_img, int(self.overlay.orig_cols/2), int(self.overlay.orig_rows/2),
			                      self.overlay.img)
			tmp = self.orig_img
			self.orig_img = self.orig_color_img
			self.change_size(self.radius_scale * 1.13, self.radius_scale * 1.13, inter_type=cv2.INTER_LINEAR)
			self.orig_color_img = np.copy(self.img)
			self.orig_img = tmp
			self.circle_frames.append([])

			self.orig_color_slider = np.copy(self.slider_circle.orig_img)
			tmp = self.slider_circle.orig_img
			self.add_color(self.orig_color_slider, color)
			self.overlayhitcircle(self.orig_color_slider, int(self.slidercircleoverlay.orig_cols/2), int(self.slidercircleoverlay.orig_rows/2),
			                      self.slidercircleoverlay.img)

			self.slider_circle.orig_img = self.orig_color_slider
			self.slider_circle.change_size(self.radius_scale * 1.13, self.radius_scale * 1.13, inter_type=cv2.INTER_LINEAR)
			self.slider_circle.orig_rows = self.slider_circle.orig_img.shape[0]
			self.slider_circle.orig_cols = self.slider_circle.orig_img.shape[1]
			self.orig_color_slider = np.copy(self.slider_circle.img)
			self.slider_circle.orig_img = tmp

			self.slidercircle_frames.append({})   # so to find the right combo will be faster

			for x in range(1, self.maxcombo[c] + 1):
				self.number_drawer.draw(self.img, x, self.gap)

				if x in self.slider_combo:
					self.number_drawer.draw(self.slider_circle.img, x, self.gap)
					self.slidercircle_frames[-1][x] = []
				alpha = 0
				self.circle_frames[-1].append([])
				for i in range(len(self.approachCircle.approach_frames)):
					approach_circle = np.copy(self.approachCircle.approach_frames[i])

					x_offset = int(approach_circle.shape[1] / 2)
					y_offset = int(approach_circle.shape[0] / 2)

					if x in self.slider_combo:
						approach_slider = np.copy(approach_circle)
						self.overlay_approach(approach_slider, x_offset, y_offset, self.slider_circle.img)
						approach_slider[:, :, 3] = approach_slider[:, :, 3] * (alpha / 100)
						self.to_3channel(approach_slider)
						self.slidercircle_frames[-1][x].append(approach_slider)

					self.overlay_approach(approach_circle, x_offset, y_offset, self.img)
					approach_circle[:, :, 3] = approach_circle[:, :, 3] * (alpha / 100)
					self.to_3channel(approach_circle)

					self.circle_frames[-1][-1].append(approach_circle)
					alpha = min(100, alpha + self.opacity_interval)

				self.img = np.copy(self.orig_color_img)
				self.slider_circle.img = np.copy(self.orig_color_slider)
		print("done")
		del self.approachCircle

	def add_circle(self, x, y, combo_color, combo_number,  isSlider=0):
		self.circles.append([x, y, self.time_preempt, -1, combo_color, combo_number, isSlider])

	def add_to_frame(self, background):
		i = len(self.circles) - 1
		while i > -1:
			self.circles[i][2] -= self.interval
			self.circles[i][3] += 1
			if self.circles[i][2] <= 0:
				del self.circles[i]
				break  # break right after since self.circles[i][2] < 0 means i reached 0 so no need to continue the loop

			color = self.circles[i][4] - 1
			number = self.circles[i][5]
			opacity_index = self.circles[i][3]
			if self.circles[i][6]:
				try:
					self.img = self.slidercircle_frames[color][number][opacity_index]
				except Exception:
					print("color:", len(self.circle_frames), color)
					print("number", len(self.circle_frames[color]), number)
					print("opacity_index", len(self.circle_frames[color][number]), opacity_index)
			else:
				self.img = self.circle_frames[color][number - 1][opacity_index]
			super().add_to_frame(background, self.circles[i][0], self.circles[i][1])

			i -= 1


class Slider:
	def __init__(self, slidermultiplier, time_preempt, opacity_interval, scale):
		self.sliders = []
		self.slidermutiplier = slidermultiplier
		self.time_preempt = time_preempt
		self.interval = 1000/60
		self.opacity_interval = opacity_interval
		self.scale = scale

	def change_size(self, new_row, new_col, image, inter_type=cv2.INTER_AREA):
		n_rows = int(new_row * image.shape[0])
		n_rows -= int(n_rows % 2 == 1)  # need to be even
		n_cols = int(new_col * image.shape[1])
		n_cols -= int(n_cols % 2 == 1)  # need to be even
		image = cv2.resize(image, (n_cols, n_rows), interpolation=inter_type)
		return image

	def add_slider(self, image, x_offset, y_offset, x_pos, y_pos, pixel_legnth, beat_duration):
		slider_duration = beat_duration * pixel_legnth / (100 * self.slidermutiplier)

		image = self.change_size(self.scale, self.scale, image)
		# to_frame always draw from the top left corner of the image, meanwhile we want it to draw from the slider's start pos
		x_offset = int(x_offset * self.scale)
		y_offset = int(y_offset * self.scale)
		self.sliders.append([image, x_pos - x_offset, y_pos - y_offset, slider_duration + self.time_preempt, 0])

	# crop everything that goes outside the screen
	def checkOverdisplay(self, pos1, pos2, limit):
		start = 0
		end = pos2 - pos1
		if pos1 < 0:
			start = -pos1
			pos1 = 0
		if pos2 >= limit:
			end -= pos2 - limit + 1
			pos2 = limit - 1
		return pos1, pos2, start, end

	def to_frame(self, img, background, x_offset, y_offset):
		# to_3channel done in generate_slider.py
		y1, y2 = y_offset, y_offset + img.shape[0]
		x1, x2 = x_offset, x_offset + img.shape[1]

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])
		alpha_s = img[ystart:yend, xstart:xend, 3] / 255.0
		alpha_l = 1.0 - alpha_s

		for c in range(3):
			background[y1:y2, x1:x2, c] = (
					img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])

	def add_to_frame(self, background):
		i = len(self.sliders) - 1
		while i > - 1:
			self.sliders[i][3] -= self.interval
			self.sliders[i][4] = min(100, self.sliders[i][4] + self.opacity_interval)
			if self.sliders[i][3] <= 0:
				del self.sliders[i]
				break  # same as circle add_to_frame reason
			cur_img = np.copy(self.sliders[i][0])
			cur_img[:, :, 0:3] *= self.sliders[i][4]/100
			self.to_frame(cur_img, background, self.sliders[i][1], self.sliders[i][2])
			i -= 1


