from Objects.abstracts import *
from Curves.curve import *


sliderb = "sliderb.png"
sliderfollowcircle = "sliderfollowcircle.png"
sliderscorepiont = "sliderscorepoint.png"
default_size = 128


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
		self.slidermax_index = len(self.sliderfollow_fadeout) - 1

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

		# if sliderfollowcircle is smaller than sliderball ( possible when fading in the sliderfollowcircle), then create
		# a blank image with sliderball shape and put sliderfollowcircle at the center of that image.
		if sliderball.shape[0] > follow.shape[0]:
			new_img = np.zeros(sliderball.shape)
			y1, y2 = int(new_img.shape[0] / 2 - follow.shape[0] / 2), int(new_img.shape[0] / 2 + follow.shape[0] / 2)
			x1, x2 = int(new_img.shape[1] / 2 - follow.shape[1] / 2), int(new_img.shape[1] / 2 + follow.shape[1] / 2)
			new_img[y1:y2, x1:x2, :] = follow[:, :, :]
			follow = new_img

		#  find center
		y1, y2 = int(follow.shape[0]/2 - sliderball.shape[0]/2), int(follow.shape[0]/2 + sliderball.shape[0]/2)
		x1, x2 = int(follow.shape[1]/2 - sliderball.shape[1]/2), int(follow.shape[1]/2 + sliderball.shape[1]/2)

		alpha_s = sliderball[:, :, 3] * self.divide_by_255
		alpha_l = 1 - alpha_s
		for c in range(3):
			follow[y1:y2, x1:x2, c] = sliderball[:, :, c] * alpha_s + alpha_l * follow[y1:y2, x1:x2, c]
		follow[y1:y2, x1:x2, 3] = follow[y1:y2, x1:x2, 3] * alpha_l + sliderball[:, :, 3]

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

				# if it's the first loop then add sliderfollowcircle without sliderball for the fadeout
				if c == 1:
					follow_img = np.copy(orig_sfollow)
					self.to_3channel(follow_img)
					self.sliderfollow_fadeout.append(follow_img)

				# add sliderball to sliderfollowcircle because it will optimize the render time since we don't need to
				# add to frame twice
				self.ballinhole(orig_sfollow, orig_color_sb)
				self.to_3channel(orig_sfollow)
				self.sliderb_frames[-1].append(np.copy(orig_sfollow))
				cur_scale -= scale_interval
				cur_alpha -= alpha_interval
		self.sliderfollow_fadeout.append(np.zeros((2, 2, 4)))


	def add_slider(self, osu_d, x_pos, y_pos, beat_duration):
		image = osu_d["slider_img"]
		x_offset, y_offset = osu_d["x_offset"], osu_d["y_offset"]
		pixel_length, color = osu_d["pixel_length"], osu_d["combo_color"]
		slider_duration = beat_duration * pixel_length / (100 * self.slidermutiplier)

		# bezier info to calculate curve for sliderball. Actually the first three info is needed for the curve computing
		# function, but we add stack to reduce sliders list size
		b_info = (osu_d["slider_type"], osu_d["ps"], osu_d["pixel_length"], osu_d["stacking"])

		# [image, x, y, current duration, opacity, color, sliderball index, original duration, bezier info, cur_repeated, repeated]
		self.sliders.append([image, x_pos-x_offset, y_pos-y_offset, slider_duration + self.time_preempt,
		                     0, color, self.slidermax_index-1, slider_duration, b_info, 1, osu_d["repeated"]])

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
				self.sliders[i][6] = min(self.slidermax_index, self.sliders[i][6] + 0.65)

				# reduce opacity of slider
				self.sliders[i][4] = max(-self.opacity_interval, self.sliders[i][4] - 4*self.opacity_interval)


		self.sliders[i][4] = min(90, self.sliders[i][4] + self.opacity_interval)
		cur_img = np.copy(self.sliders[i][0])
		cur_img[:, :, :] = cur_img[:, :, :] * (self.sliders[i][4]/100)
		self.to_frame(cur_img, background, self.sliders[i][1], self.sliders[i][2])


		if 0 < self.sliders[i][3] <= self.sliders[i][7]:
			t = self.sliders[i][3]/self.sliders[i][7]

			# if sliderball is going forward
			if going_forward:
				t = 1 - t

			cur_pos = baiser(round(t, 3))
			x = int((cur_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown
			color = self.sliders[i][5]-1
			index = self.sliders[i][6]
			self.to_frame2(self.sliderb_frames[color][index], background, x, y)
			self.sliders[i][6] = max(0, self.sliders[i][6] - 1)
