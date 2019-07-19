from Objects.abstracts import *
from Curves.curve import *


hitcircle = "hitcircle.png"
hitcircleoverlay = "hitcircleoverlay.png"
sliderstartcircleoverlay = "sliderstartcircleoverlay.png"
sliderstartcircle = "sliderstartcircle.png"
approachcircle = "approachcircle.png"
sliderb = "sliderb.png"
sliderfollowcircle = "sliderfollowcircle.png"
sliderscorepiont = "sliderscorepoint.png"
default_size = 128


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


class ApproachCircle(ACircle):
	def __init__(self, filename, hitcircle_cols, hitcircle_rows, scale, time_preempt, interval):
		ACircle.__init__(self, filename, hitcircle_cols, hitcircle_rows)
		self.scale = scale
		self.time_preempt = round(time_preempt)
		self.interval = int(interval)
		self.approach_frames = []
		self.to_3channel()
		self.prepare_sizes()

	def prepare_sizes(self):
		scale = 3
		for time_left in range(self.time_preempt, 0, -self.interval):
			scale -= 2 * self.interval / self.time_preempt
			self.change_size(scale * self.scale, scale * self.scale)
			self.approach_frames.append(self.img)

	def add_to_frame(self, background, x_offset, y_offset, time_left):
		self.img = self.approach_frames[int((self.time_preempt - time_left) / self.interval)]
		super().add_to_frame(background, x_offset, y_offset)


class CircleOverlay(ACircle):
	def __init__(self, filename, hitcircle_cols, hitcircle_rows):
		ACircle.__init__(self, filename, hitcircle_cols, hitcircle_rows)


class SliderCircleOverlay(ACircle):
	def __init__(self, filename, hitcircle_cols, hitcircle_rows):
		ACircle.__init__(self, filename, hitcircle_cols, hitcircle_rows)


class CircleSlider(ACircle):
	def __init__(self, filename, hitcircle_cols, hitcircle_rows):
		ACircle.__init__(self, filename, hitcircle_cols, hitcircle_rows)


class PrepareCircles(Images):
	def __init__(self, slider_combo, path, diff, scale, maxcombo, gap, colors):
		"""
		:param path: str where is the skin folder
		:param diff: dict, contains ApproachRate, CircleSize, OverallDifficulty, HPDrain
		:param scale: float scale of current screen res with 512x384
		:param maxcombo: dict, biggest number we need to overlap, for preparing_circle, where we overlap every number with every circle
		:param gap: int, gap between 2 digits
		"""
		Images.__init__(self, path + hitcircle)
		self.overlay_filename = path + hitcircleoverlay
		self.slideroverlay_filename = path + sliderstartcircleoverlay
		self.diff = diff
		self.circles = []
		self.interval = 1000 / 60  # ms between 2 frames
		self.overlay_scale = 1.05
		self.ar = diff["ApproachRate"]
		self.cs = (54.4 - 4.48 * diff["CircleSize"]) * scale

		self.calculate_ar()
		self.load_circle()

		self.maxcolors = colors["ComboNumber"]
		self.colors = colors
		self.maxcombo = maxcombo
		self.gap = int(gap * self.radius_scale)

		self.slider_combo = slider_combo
		self.slider_circle = CircleSlider(path + sliderstartcircle, self.orig_cols, self.orig_rows)

		self.number_drawer = Number(self.cs * 0.9, path, default_size)
		self.approachCircle = ApproachCircle(path + approachcircle, self.orig_cols, self.orig_rows, self.radius_scale,
		                                     self.time_preempt, self.interval)

		self.create_black_circle()

		self.circle_frames = []
		self.slidercircle_frames = []
		self.circle_fadeout = []
		self.prepare_circle()

	def create_black_circle(self):
		# black support so that slider color won't affect hitcircleslider color cuz alpha when it begins to appear
		self.circle_supporter = np.copy(self.orig_img)
		self.add_color(self.circle_supporter, (0, 0, 0))
		tmp = self.orig_img
		self.orig_img = self.circle_supporter
		self.change_size(self.radius_scale, self.radius_scale, inter_type=cv2.INTER_LINEAR)
		self.circle_supporter = self.img
		self.orig_img = tmp
		self.img = np.copy(self.orig_img)
		cv2.addWeighted(self.circle_supporter, 1, self.circle_supporter, 1, 1, self.circle_supporter)  # increase opacity
		cv2.addWeighted(self.circle_supporter, 1, self.circle_supporter, 1, 1, self.circle_supporter)

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
		self.opacity_interval = int(100 * self.interval / self.fade_in)

	def add_color(self, image, color):
		red = color[0]*self.divide_by_255
		green = color[1]*self.divide_by_255
		blue = color[2]*self.divide_by_255
		image[:, :, 0] = np.multiply(image[:, :, 0], blue, casting='unsafe')
		image[:, :, 1] = np.multiply(image[:, :, 1], green, casting='unsafe')
		image[:, :, 2] = np.multiply(image[:, :, 2], red, casting='unsafe')
		# image[image > 255] = 255

	def load_circle(self):
		self.overlay = CircleOverlay(self.overlay_filename, self.orig_cols, self.orig_rows)
		self.slidercircleoverlay = SliderCircleOverlay(self.slideroverlay_filename, self.orig_cols, self.orig_rows)
		self.radius_scale = self.cs * self.overlay_scale * 2 / default_size

	def overlayhitcircle(self, overlay, hitcircle_image):
		# still ned 4 channels so cannot do to_3channel before.
		y1, y2 = int(overlay.shape[0]/2 - hitcircle_image.shape[0]/2), int(overlay.shape[0]/2 + hitcircle_image.shape[0]/2)
		x1, x2 = int(overlay.shape[1]/2 - hitcircle_image.shape[1]/2), int(overlay.shape[1]/2 + hitcircle_image.shape[1]/2)

		alpha_s = overlay[y1:y2, x1:x2, 3] * self.divide_by_255
		alpha_l = 1 - alpha_s

		for c in range(3):
			overlay[y1:y2, x1:x2, c] = hitcircle_image[:, :, c] * alpha_l + \
			                              alpha_s * overlay[y1:y2, x1:x2, c]
		overlay[y1:y2, x1:x2, 3] = overlay[y1:y2, x1:x2, 3] + alpha_l * hitcircle_image[:, :, 3]

	def overlay_approach(self, background, x_offset, y_offset, circle_img, alpha):
		# still ned 4 channels so cannot do to_3channel before.
		y1, y2 = y_offset - int(circle_img.shape[0] / 2), y_offset + int(circle_img.shape[0] / 2)
		x1, x2 = x_offset - int(circle_img.shape[1] / 2), x_offset + int(circle_img.shape[1] / 2)

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])

		alpha_s = background[y1:y2, x1:x2, 3] * self.divide_by_255
		alpha_l = 1 - alpha_s
		for c in range(3):
			background[y1:y2, x1:x2, c] = circle_img[ystart:yend, xstart:xend, c] * alpha_l + \
			                              background[y1:y2, x1:x2, c]
		background[y1:y2, x1:x2, 3] = background[y1:y2, x1:x2, 3] + circle_img[ystart:yend, xstart:xend, 3] * alpha_l
		background[:, :, :] = background[:, :, :] * (alpha/100)

	def to_3channel(self, image):
		# convert 4 channel to 3 channel, so we can ignore alpha channel, this will optimize the time of add_to_frame
		# where we needed to do each time alpha_s * img[:, :, 0:3]. Now we don't need to do it anymore
		alpha_s = image[:, :, 3] * self.divide_by_255
		for c in range(3):
			image[:, :, c] = image[:, :, c] * alpha_s

	def change_size2(self, img, new_col, new_row):
		n_rows = int(new_row * img.shape[1])
		n_rows -= int(n_rows % 2 == 1)  # need to be even
		n_cols = int(new_col * img.shape[0])
		n_cols -= int(n_cols % 2 == 1)  # need to be even
		return cv2.resize(img, (n_cols, n_rows), interpolation=cv2.INTER_LINEAR)

	def prepare_circle(self):
		# prepare every single frame before entering the big loop, this will save us a ton of time since we don't need
		# to overlap number, circle overlay and approach circle every single time.
		for c in range(1, self.maxcolors + 1):
			color = self.colors["Combo" + str(c)]

			orig_overlay_img = np.copy(self.overlay.img)
			orig_color_img = np.copy(self.orig_img)
			self.add_color(orig_color_img, color)
			self.overlayhitcircle(orig_overlay_img, orig_color_img)
			orig_overlay_img = self.change_size2(orig_overlay_img, self.radius_scale, self.radius_scale)
			self.to_3channel(orig_overlay_img)
			self.img = np.copy(orig_overlay_img)
			self.circle_frames.append([])

			self.circle_fadeout.append([])
			for x in range(100, 140, 4):
				size = x/100
				im = np.copy(self.img)
				im[:, :, :] = im[:, :, :] * (1 - (x - 100)/40)
				self.circle_fadeout[-1].append(self.change_size2(im, size, size))

			orig_color_slider = np.copy(self.slider_circle.orig_img)
			orig_overlay_slider = np.copy(self.slidercircleoverlay.img)
			self.add_color(orig_color_slider, color)
			self.overlayhitcircle(orig_overlay_slider, orig_color_slider)
			orig_overlay_slider = self.change_size2(orig_overlay_slider, self.radius_scale, self.radius_scale)
			self.to_3channel(orig_overlay_slider)
			self.slider_circle.img = np.copy(orig_overlay_slider)
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
					self.add_color(approach_circle, color)
					x_offset = int(approach_circle.shape[1] / 2)
					y_offset = int(approach_circle.shape[0] / 2)

					if x in self.slider_combo:
						approach_slider = np.copy(approach_circle)
						self.overlay_approach(approach_slider, x_offset, y_offset, self.slider_circle.img, alpha)
						# approach_slider[:, :, 3] = approach_slider[:, :, 3] * (alpha / 100)
						# self.to_3channel(approach_slider)
						self.slidercircle_frames[-1][x].append(approach_slider)

					self.overlay_approach(approach_circle, x_offset, y_offset, self.img, alpha)
					# approach_circle[:, :, 3] = approach_circle[:, :, 3] * (alpha / 100)
					# self.to_3channel(approach_circle)

					self.circle_frames[-1][-1].append(approach_circle)
					alpha = min(100, alpha + self.opacity_interval)
				if x in self.slider_combo:
					self.slidercircle_frames[-1][x].append(self.slider_circle.img)
				self.circle_frames[-1][-1].append(self.img)  # for late tapping

				self.img = np.copy(orig_overlay_img)
				self.slider_circle.img = np.copy(orig_overlay_slider)
		print("done")
		del self.approachCircle

	def add_circle(self, x, y, combo_color, combo_number,  object_type=0):
		self.circles.append([x, y, self.time_preempt, -1, combo_color, combo_number, object_type, 0])

	def add_to_frame(self, background, i):
		color = self.circles[i][4] - 1
		self.circles[i][2] -= self.interval
		if self.circles[i][2] <= -self.interval * 4:
			if self.circles[i][6]:
				return
			self.img = self.circle_fadeout[color][self.circles[i][7]]
			self.circles[i][7] += 1
			super().add_to_frame(background, self.circles[i][0], self.circles[i][1])
			return
		self.circles[i][3] += 1
		number = self.circles[i][5]
		if self.circles[i][6]:
			opacity_index = min(self.circles[i][3], len(self.slidercircle_frames[color][number]) - 1)
			self.img = self.circle_supporter
			super().add_to_frame(background, self.circles[i][0], self.circles[i][1])
			self.img = self.slidercircle_frames[color][number][opacity_index]
		else:
			opacity_index = min(self.circles[i][3], len(self.circle_frames[color][number]) - 1)
			self.img = self.circle_frames[color][number - 1][opacity_index]
		super().add_to_frame(background, self.circles[i][0], self.circles[i][1])


class PrepareSlider:
	def __init__(self, path, diff, time_preempt, opacity_interval, scale, colors, movedown, moveright):
		self.path = path
		self.sliders = []
		self.movedown = movedown
		self.moveright = moveright
		self.maxcolors = colors["ComboNumber"]
		self.colors = colors
		self.cs = (54.4 - 4.48 * diff["CircleSize"]) * scale
		self.slidermutiplier = diff["SliderMultiplier"]
		self.time_preempt = time_preempt
		self.interval = 1000/60
		self.opacity_interval = opacity_interval
		self.scale = scale
		self.divide_by_255 = 1/255.0
		self.sliderb_frames = []
		self.sliderfollow_fadeout = []
		self.load_sliderballs()
		self.prepare_sliderball()
		self.slidermax_index = len(self.sliderb_frames[0]) - 1

	def load_sliderballs(self):
		self.sliderb = cv2.imread(self.path + sliderb, -1)
		self.sliderfollowcircle = cv2.imread(self.path + sliderfollowcircle, -1)
		self.followscale = default_size/self.sliderfollowcircle.shape[0]
		self.radius_scale = self.cs * 2 / default_size
		self.sliderb = self.change_size2(self.sliderb, self.radius_scale, self.radius_scale)
		self.sliderfollowcircle = self.change_size2(self.sliderfollowcircle, self.radius_scale, self.radius_scale)

	def add_color(self, image, color):
		red = color[0]*self.divide_by_255
		green = color[1]*self.divide_by_255
		blue = color[2]*self.divide_by_255
		image[:, :, 0] = np.multiply(image[:, :, 0], blue, casting='unsafe')
		image[:, :, 1] = np.multiply(image[:, :, 1], green, casting='unsafe')
		image[:, :, 2] = np.multiply(image[:, :, 2], red, casting='unsafe')

	def to_3channel(self, image):
		# convert 4 channel to 3 channel, so we can ignore alpha channel, this will optimize the time of add_to_frame
		# where we needed to do each time alpha_s * img[:, :, 0:3]. Now we don't need to do it anymore
		alpha_s = image[:, :, 3] * self.divide_by_255
		for c in range(3):
			image[:, :, c] = image[:, :, c] * alpha_s

	def change_size2(self, img, new_col, new_row):
		n_rows = int(new_row * img.shape[1])
		n_rows -= int(n_rows % 2 == 1)  # need to be even
		n_cols = int(new_col * img.shape[0])
		n_cols -= int(n_cols % 2 == 1)  # need to be even
		return cv2.resize(img, (n_cols, n_rows), interpolation=cv2.INTER_LINEAR)

	def ballinhole(self, follow, sliderball):
		# still ned 4 channels so cannot do to_3channel before.
		if sliderball.shape[0] > follow.shape[0]:
			new_img = np.zeros(sliderball.shape)
			y1, y2 = int(new_img.shape[0] / 2 - follow.shape[0] / 2), int(new_img.shape[0] / 2 + follow.shape[0] / 2)
			x1, x2 = int(new_img.shape[1] / 2 - follow.shape[1] / 2), int(new_img.shape[1] / 2 + follow.shape[1] / 2)
			new_img[y1:y2, x1:x2, :] = follow[:, :, :]
			follow = new_img
		y1, y2 = int(follow.shape[0]/2 - sliderball.shape[0]/2), int(follow.shape[0]/2 + sliderball.shape[0]/2)
		x1, x2 = int(follow.shape[1]/2 - sliderball.shape[1]/2), int(follow.shape[1]/2 + sliderball.shape[1]/2)

		alpha_s = sliderball[:, :, 3] * self.divide_by_255
		alpha_l = 1 - alpha_s
		for c in range(3):
			follow[y1:y2, x1:x2, c] = sliderball[:, :, c] * alpha_s + alpha_l * follow[y1:y2, x1:x2, c]
		follow[y1:y2, x1:x2, 3] = follow[y1:y2, x1:x2, 3] * alpha_l + sliderball[:, :, 3]

	def prepare_sliderball(self):
		follow_fadein = 125
		for c in range(1, self.maxcolors + 1):
			color = self.colors["Combo" + str(c)]
			orig_color_sb = np.copy(self.sliderb)
			self.add_color(orig_color_sb, color)
			self.sliderb_frames.append([])

			scale_interval = round((1 - self.followscale) * self.interval / follow_fadein, 2)
			cur_scale = 1
			alpha_interval = round(self.interval / follow_fadein, 2)
			cur_alpha = 1
			for x in range(follow_fadein, 0, -int(self.interval)):
				orig_sfollow = self.change_size2(self.sliderfollowcircle, cur_scale, cur_scale)
				orig_sfollow[:, :, 3] = orig_sfollow[:, :, 3] * cur_alpha
				if c == 1:
					follow_img = np.copy(orig_sfollow)
					self.to_3channel(follow_img)
					self.sliderfollow_fadeout.append(follow_img)
				self.ballinhole(orig_sfollow, orig_color_sb)
				self.to_3channel(orig_sfollow)
				self.sliderb_frames[-1].append(np.copy(orig_sfollow))
				cur_scale -= scale_interval
				cur_alpha -= alpha_interval

	def add_slider(self, osu_d, x_pos, y_pos, beat_duration):
		image = osu_d["slider_img"]
		x_offset, y_offset = osu_d["x_offset"], osu_d["y_offset"]
		pixel_length, color = osu_d["pixel_length"], osu_d["combo_color"]
		slider_duration = beat_duration * pixel_length / (100 * self.slidermutiplier)
		b_info = (osu_d["slider_type"], osu_d["ps"], osu_d["pixel_length"], osu_d["stacking"])
		# [image, x, y, current duration, opacity, color, sliderball index, original duration, bezier info]
		self.sliders.append([image, x_pos-x_offset, y_pos-y_offset, slider_duration + self.time_preempt,
		                     0, color, self.slidermax_index, slider_duration, b_info])

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
		alpha_s = img[ystart:yend, xstart:xend, 3] * self.divide_by_255
		alpha_l = 1.0 - alpha_s

		for c in range(3):
			background[y1:y2, x1:x2, c] = (
					img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])

	def to_frame2(self, img, background, x_offset, y_offset):
		# need to do to_3channel first.
		y1, y2 = y_offset - int(img.shape[0] / 2), y_offset + int(img.shape[0] / 2)
		x1, x2 = x_offset - int(img.shape[1] / 2), x_offset + int(img.shape[1] / 2)

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])

		alpha_s = img[ystart:yend, xstart:xend, 3] * self.divide_by_255
		alpha_l = 1.0 - alpha_s
		for c in range(3):
			background[y1:y2, x1:x2, c] = (
					img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])

	def add_to_frame(self, background, i):
		self.sliders[i][3] -= self.interval
		if self.sliders[i][3] <= 0:
			baiser = Curve.from_kind_and_points(*self.sliders[i][8][0:3])
			cur_pos = baiser(1)
			x = int((cur_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown
			index = int(self.sliders[i][6])
			self.to_frame2(self.sliderfollow_fadeout[index], background, x, y)
			self.sliders[i][6] = min(self.slidermax_index, self.sliders[i][6] + 0.65)
			self.sliders[i][4] = max(0, self.sliders[i][4] - 4*self.opacity_interval)

		self.sliders[i][4] = min(100, self.sliders[i][4] + self.opacity_interval)
		cur_img = np.copy(self.sliders[i][0])
		cur_img[:, :, :] = cur_img[:, :, :] * (self.sliders[i][4]/100)
		self.to_frame(cur_img, background, self.sliders[i][1], self.sliders[i][2])

		if 0 < self.sliders[i][3] <= self.sliders[i][7]:
			baiser = Curve.from_kind_and_points(*self.sliders[i][8][0:3])
			t = 1 - self.sliders[i][3]/self.sliders[i][7]
			cur_pos = baiser(t)
			x = int((cur_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown
			color = self.sliders[i][5]-1
			index = self.sliders[i][6]
			self.to_frame2(self.sliderb_frames[color][index], background, x, y)
			self.sliders[i][6] = max(0, self.sliders[i][6] - 1)


class HitObjectManager:
	def __init__(self, slider_combo, path, diff, scale, maxcombo, gap, colors, movedown, moveright):
		self.preparecircle = PrepareCircles(slider_combo, path, diff, scale, maxcombo, gap, colors)
		self.time_preempt = self.preparecircle.time_preempt
		opacity = self.preparecircle.opacity_interval
		self.prepareslider = PrepareSlider(path, diff, self.time_preempt, opacity, scale, colors, movedown, moveright)
		self.hitobject = []
		self.interval = 1000 / 60
		self.IS_CIRCLE = 0
		self.IS_CIRCLESLIDER = 1
		self.IS_SLIDER = 2

	def add_slider(self, osu_d, x_pos, y_pos, beat_duration):
		self.prepareslider.add_slider(osu_d, x_pos, y_pos, beat_duration)
		sliderduration = self.prepareslider.sliders[-1][3]
		self.hitobject.append([self.IS_SLIDER, sliderduration])

	def add_circle(self, x, y, combo_color, combo_number,  object_type=0):
		self.preparecircle.add_circle(x, y, combo_color, combo_number,  object_type)
		circleduration = self.time_preempt
		self.hitobject.append([object_type, circleduration])

	def add_to_frame(self, background):
		slider_index = len(self.prepareslider.sliders)
		circle_index = len(self.preparecircle.circles)
		i = len(self.hitobject) - 1

		while i > -1:
			self.hitobject[i][1] -= self.interval
			if self.hitobject[i][0] == self.IS_CIRCLE or self.hitobject[i][0] == self.IS_CIRCLESLIDER:
				circle_index -= 1
				if self.hitobject[i][1] < -self.interval * 14:  # for late click
					del self.preparecircle.circles[circle_index]
					del self.hitobject[i]
					circle_index -= 1
					i -= 1
					continue
				self.preparecircle.add_to_frame(background, circle_index)
			else:
				slider_index -= 1
				if self.hitobject[i][1] < -self.interval * 10:  # for effect
					del self.prepareslider.sliders[slider_index]
					del self.hitobject[i]
					slider_index -= 1
					i -= 1
					continue
				self.prepareslider.add_to_frame(background, slider_index)
			i -= 1


