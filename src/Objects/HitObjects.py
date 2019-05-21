from Objects.abstracts import *
from Objects.prepare import _main


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


class CircleSlider(Images):
	def __init__(self, filename, radius_scale):
		Images.__init__(self, filename)
		# cuz overlay hitcircle
		self.change_size(radius_scale * 1.13, radius_scale * 1.13, inter_type=cv2.INTER_LINEAR)
		max_scale = 255/np.max(self.img[:, :, 3])
		self.img[:, :, 3] = self.img[:, :, 3] * max_scale
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]


class Circles(Images):
	def __init__(self, filename, overlay_filename, slidercircle_filename, slider_combo,
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

		self.circle_frames = {}
		self.slidercircle_frames = {}
		_main(self.maxcolors, self.circle_frames, self.slidercircle_frames, self.orig_img, self.overlay, self.radius_scale, self.img, self.number_drawer, self.gap,
		      self.slider_combo, self.approachCircle, self.opacity_interval, self.overlay_filename, self.orig_cols, self.orig_rows, self.default_circle_size, self.cs, self.colors, self.slider_circle, self.maxcombo)
		print("done")
		ray.shutdown()
		self.maxcolors.fuckyou

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

	def load_circle(self):
		self.overlay = CircleOverlay(self.overlay_filename)

		cur_radius = self.orig_cols / 2
		self.radius_scale = self.cs / cur_radius
		self.default_circle_size = self.orig_rows  # save for number class

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


