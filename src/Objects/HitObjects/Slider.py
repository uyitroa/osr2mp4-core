from Curves.generate_slider import GenerateSlider
from Objects.abstracts import *
from Curves.curve import *

sliderb = "sliderb.png"
sliderfollowcircle = "sliderfollowcircle.png"
sliderscorepiont = "sliderscorepoint.png"
reversearrow = "reversearrow.png"
default_size = 128


class ReverseArrow(Images):
	def __init__(self, path, scale, simulate):
		Images.__init__(self, path + reversearrow, simulate=simulate)
		self.to_square()
		self.change_size(scale * 1.1, scale * 1.1)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.orig_img.shape[0]
		self.orig_cols = self.orig_img.shape[1]
		self.to_3channel()

	def to_square(self):
		max_length = int(np.sqrt(self.img.shape[0] ** 2 + self.img.shape[1] ** 2))
		square = np.zeros((max_length, max_length, self.img.shape[2]))
		y1, y2 = int(max_length / 2 - self.orig_rows / 2), int(max_length / 2 + self.orig_rows / 2)
		x1, x2 = int(max_length / 2 - self.orig_cols / 2), int(max_length / 2 + self.orig_cols / 2)
		square[y1:y2, x1:x2, :] = self.img[:, :, :]
		self.orig_img = square
		self.orig_rows, self.orig_cols = max_length, max_length

	def rotate_image(self, angle):
		image_center = tuple(np.array(self.img.shape[1::-1]) / 2)
		rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
		result = cv2.warpAffine(self.img, rot_mat, self.img.shape[1::-1], flags=cv2.INTER_LINEAR)
		return result


class PrepareSlider:
	def __init__(self, path, diff, scale, skin, movedown, moveright, simulate=False):
		self.path = path
		self.simulate = simulate
		self.sliders = {}
		self.arrows = {}
		self.movedown = movedown
		self.moveright = moveright
		self.maxcolors = skin.colours["ComboNumber"]
		self.colors = skin.colours
		self.interval = 1000 / 60
		self.cs = (54.4 - 4.48 * diff["CircleSize"])

		self.sliderborder = skin.colours["SliderBorder"]
		self.slideroverride = skin.colours["SliderTrackOverride"]
		self.gs = GenerateSlider(self.sliderborder, self.slideroverride, self.cs, scale)

		self.cs = self.cs * scale
		self.ar = diff["ApproachRate"]
		self.slidermutiplier = diff["SliderMultiplier"]
		self.calculate_ar()

		self.scale = scale
		self.divide_by_255 = 1 / 255.0
		self.sliderb_frames = []
		self.sliderfollow_fadeout = []
		self.load_sliderballs()
		self.prepare_sliderball()
		self.slidermax_index = len(self.sliderfollow_fadeout) - 1

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

	def load_sliderballs(self):
		self.sliderb = cv2.imread(self.path + sliderb, -1)
		self.sliderfollowcircle = cv2.imread(self.path + sliderfollowcircle, -1)

		self.followscale = default_size / self.sliderfollowcircle.shape[0]
		self.radius_scale = self.cs * 2 / default_size

		self.reversearrow = ReverseArrow(self.path, self.radius_scale, self.simulate)
		self.sliderb = self.change_size2(self.sliderb, self.radius_scale, self.radius_scale)
		self.sliderfollowcircle = self.change_size2(self.sliderfollowcircle, self.radius_scale, self.radius_scale)

		self.slidertick = Images(self.path + sliderscorepiont, self.radius_scale, simulate=self.simulate)
		self.slidertick.to_3channel()

	def add_color(self, image, color):
		red = color[0] * self.divide_by_255
		green = color[1] * self.divide_by_255
		blue = color[2] * self.divide_by_255
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

		# if sliderfollowcircle is smaller than sliderball ( possible when fading in the sliderfollowcircle), then create
		# a blank image with sliderball shape and put sliderfollowcircle at the center of that image.
		if sliderball.shape[0] > follow.shape[0]:
			new_img = np.zeros(sliderball.shape)
			y1, y2 = int(new_img.shape[0] / 2 - follow.shape[0] / 2), int(new_img.shape[0] / 2 + follow.shape[0] / 2)
			x1, x2 = int(new_img.shape[1] / 2 - follow.shape[1] / 2), int(new_img.shape[1] / 2 + follow.shape[1] / 2)
			new_img[y1:y2, x1:x2, :] = follow[:, :, :]
			follow = new_img

		#  find center
		y1, y2 = int(follow.shape[0] / 2 - sliderball.shape[0] / 2), int(follow.shape[0] / 2 + sliderball.shape[0] / 2)
		x1, x2 = int(follow.shape[1] / 2 - sliderball.shape[1] / 2), int(follow.shape[1] / 2 + sliderball.shape[1] / 2)

		alpha_s = sliderball[:, :, 3] * self.divide_by_255
		alpha_l = 1 - alpha_s
		for c in range(3):
			follow[y1:y2, x1:x2, c] = sliderball[:, :, c] * alpha_s + alpha_l * follow[y1:y2, x1:x2, c]
		follow[y1:y2, x1:x2, 3] = follow[y1:y2, x1:x2, 3] * alpha_l + sliderball[:, :, 3]
		return follow

	def prepare_sliderball(self):
		follow_fadein = 125  # sliderfollowcircle zoom out zoom in time

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

				# add sliderball to sliderfollowcircle because it will optimize the render time since we don't need to
				# add to frame twice
				if c == 1:
					follow_img = np.copy(orig_sfollow)
					self.to_3channel(follow_img)
					self.sliderfollow_fadeout.append(follow_img)

				orig_sfollow = self.ballinhole(orig_sfollow, orig_color_sb)
				self.to_3channel(orig_sfollow)
				self.sliderb_frames[-1].append(np.copy(orig_sfollow))
				# if it's the first loop then add sliderfollowcircle without sliderball for the fadeout
				cur_scale -= scale_interval
				cur_alpha -= alpha_interval

	def add_slider(self, osu_d, x_pos, y_pos, cur_time):
		pixel_length, color = osu_d["pixel length"], osu_d["combo_color"]

		# bezier info to calculate curve for sliderball. Actually the first three info is needed for the curve computing
		# function, but we add stack to reduce sliders list size
		b_info = (osu_d["slider type"], osu_d["ps"], pixel_length, osu_d["stacking"], osu_d["slider ticks"])

		image, x_offset, y_offset = self.gs.get_slider_img(*b_info[0:3])

		# [image, x, y, current duration, opacity, color, sliderball index, original duration, bezier info,
		# cur_repeated, repeated, appear followcircle, tick alpha]
		self.sliders[str(osu_d["time"]) + "s"] = [image, x_pos - x_offset, y_pos - y_offset,
		                                          osu_d["duration"] + osu_d["time"] - cur_time,
		                                          0, color, self.slidermax_index, osu_d["duration"], b_info, 1,
		                                          osu_d["repeated"], 0, [0] * len(osu_d["slider ticks"])]

		pos1 = osu_d["ps"][-1]
		pos2 = osu_d["ps"][-2] if osu_d["ps"][-2].x != pos1.x or osu_d["ps"][-2].y != pos1.y else osu_d["ps"][-3]

		pos3 = osu_d["ps"][0]
		pos4 = osu_d["ps"][1] if osu_d["ps"][1].x != pos3.x or osu_d["ps"][1].y != pos3.y else osu_d["ps"][2]

		vector_x1, vector_y1 = pos2.x - pos1.x, pos2.y - pos1.y
		vector_x2, vector_y2 = pos4.x - pos3.x, pos4.y - pos3.y

		angle1 = -np.arctan2(vector_y1, vector_x1) * 180 / np.pi
		angle2 = -np.arctan2(vector_y2, vector_x2) * 180 / np.pi

		img1 = self.reversearrow.rotate_image(angle1)
		img2 = self.reversearrow.rotate_image(angle2)

		self.arrows[str(osu_d["time"]) + "s"] = [img2, img1]

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
		if self.simulate:
			return

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
		if self.simulate:
			return

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
		self.sliders[i][6] = max(0, min(self.slidermax_index, self.sliders[i][6] + self.sliders[i][11]))
		baiser = Curve.from_kind_and_points(*self.sliders[i][8][0:3])

		# if sliderball is going forward
		going_forward = self.sliders[i][9] % 2 == 1

		if self.sliders[i][3] <= 0:
			# if the slider is repeated
			if self.sliders[i][9] < self.sliders[i][10]:
				self.sliders[i][3] = self.sliders[i][7]  # reset
				self.sliders[i][9] += 1
				going_forward = not going_forward

			else:
				cur_pos = baiser(int(going_forward))  # if going_foward is true then t = 1 otherwise it's 0
				x = int((cur_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
				y = int((cur_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown

				index = int(self.sliders[i][6])

				self.to_frame2(self.sliderfollow_fadeout[index], background, x, y)

				# frame to make the sliderfollowcircle smaller, but it's smalling too fast so instead of increase index
				# by 1, we increase it by 0.65 then convert it to integer. So some frames would appear twice.
				self.sliders[i][6] = max(0, min(self.slidermax_index, self.sliders[i][6] + self.sliders[i][11]))

				# reduce opacity of slider
				self.sliders[i][4] = max(-self.opacity_interval, self.sliders[i][4] - 4 * self.opacity_interval)

		self.sliders[i][4] = min(90, self.sliders[i][4] + self.opacity_interval)
		cur_img = self.sliders[i][0][:, :, :] * (self.sliders[i][4] / 100)
		self.to_frame(cur_img, background, self.sliders[i][1], self.sliders[i][2])

		t = self.sliders[i][3] / self.sliders[i][7]

		# if sliderball is going forward
		if going_forward:
			t = 1 - t

		for count, tick_t in enumerate(self.sliders[i][8][4]):
			if self.sliders[i][9] == self.sliders[i][10]:
				if (going_forward and t > tick_t) or (not going_forward and t < tick_t):
					continue

			if self.sliders[i][3] < self.sliders[i][7] + 100:
				if count == 0 or self.sliders[i][12][count - 1] >= 0.75:
					self.sliders[i][12][count] = min(1, self.sliders[i][12][count] + 0.1)
			tick_pos = baiser(round(tick_t, 3))
			x = int((tick_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((tick_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown

			self.slidertick.img[:, :, :] = self.slidertick.orig_img[:, :, :] * (
						self.sliders[i][4] / 100 * self.sliders[i][12][count])
			self.slidertick.add_to_frame(background, x, y)

		if 0 < self.sliders[i][3] <= self.sliders[i][7]:
			cur_pos = baiser(round(t, 3))
			x = int((cur_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown
			color = self.sliders[i][5] - 1
			index = int(self.sliders[i][6])
			self.to_frame2(self.sliderb_frames[color][index], background, x, y)

		if self.sliders[i][9] < self.sliders[i][10]:
			cur_pos = baiser(int(going_forward))
			x = int((cur_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown
			arrow_img = self.arrows[i][int(going_forward)][:, :, :] * (self.sliders[i][4] / 100)
			self.to_frame2(arrow_img, background, x, y)
