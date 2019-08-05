from Objects.abstracts import *
from Curves.curve import *

sliderb = "sliderb"
sliderfollowcircle = "sliderfollowcircle"
sliderscorepiont = "sliderscorepoint.png"
reversearrow = "reversearrow.png"
default_size = 128


class ReverseArrow(AnimatedImage):
	def __init__(self, path, scale):
		AnimatedImage.__init__(self, path, reversearrow, scale, rotate=1)
		self.prepare_frames()

	def prepare_frames(self):
		for x in range(100, 80, -4):
			img = Images(self.path + self.filename, self.scale * x/10, rotate=1)
			img.to_3channel()
			self.frames.append(img)
		self.n_frame = len(self.frames)


class SliderBall(AnimatedImage):
	def __init__(self, path, scale):
		AnimatedImage.__init__(self, path, sliderb, scale, hasframes=True)


class SliderFollow(AnimatedImage):
	def __init__(self, path, scale):
		AnimatedImage.__init__(self, path, sliderfollowcircle, scale, hasframes=True, delimiter="-")


class PrepareSlider(Images):
	def __init__(self, path, diff, time_preempt, opacity_interval, scale, colors, movedown, moveright):
		self.path = path
		self.sliders = {}
		self.arrows = {}
		self.movedown = movedown
		self.moveright = moveright
		self.maxcolors = colors["ComboNumber"]
		self.colors = colors
		self.cs = (54.4 - 4.48 * diff["CircleSize"]) * scale
		self.slidermutiplier = diff["SliderMultiplier"]
		self.time_preempt = time_preempt
		self.interval = 1000 / 60
		self.opacity_interval = opacity_interval
		self.scale = scale
		self.sliderb_frames = []
		self.sliderfollow_fadeout = []
		self.load_sliderballs()
		self.prepare_sliderball()
		self.slidermax_index = len(self.sliderfollow_fadeout) - 1

	def load_sliderballs(self):
		self.radius_scale = self.cs * 2 / default_size

		self.reversearrow = ReverseArrow(self.path, self.radius_scale)
		self.sliderb = SliderBall(self.path, self.radius_scale)
		self.sliderfollowcircle = SliderFollow(self.path, self.radius_scale)

		self.followscale = default_size / self.sliderfollowcircle.nparray_at(0).shape[0]
		self.slidertick = Images(self.path + sliderscorepiont, self.radius_scale)
		self.slidertick.to_3channel()

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
			orig_color_sb = np.copy(self.sliderb.nparray_at(0))
			super().add_color(color, applytoself=False, img=orig_color_sb)

			self.sliderb_frames.append([])

			scale_interval = round((1 - self.followscale) * self.interval / follow_fadein, 2)
			cur_scale = 1
			alpha_interval = round(self.interval / follow_fadein, 2)
			cur_alpha = 1

			for x in range(follow_fadein, 0, -int(self.interval)):
				orig_sfollow = super().change_size(cur_scale, cur_scale, applytoself=False, img=self.sliderfollowcircle.nparray_at(0))
				orig_sfollow[:, :, 3] = orig_sfollow[:, :, 3] * cur_alpha

				# add sliderball to sliderfollowcircle because it will optimize the render time since we don't need to
				# add to frame twice
				if c == 1:
					follow_img = np.copy(orig_sfollow)
					super().to_3channel(applytoself=False, img=follow_img)
					self.sliderfollow_fadeout.append(follow_img)

				orig_sfollow = self.ballinhole(orig_sfollow, orig_color_sb)
				super().to_3channel(applytoself=False, img=orig_sfollow)
				self.sliderb_frames[-1].append(np.copy(orig_sfollow))
				# if it's the first loop then add sliderfollowcircle without sliderball for the fadeout
				cur_scale -= scale_interval
				cur_alpha -= alpha_interval


	def add_slider(self, osu_d, x_pos, y_pos, cur_time, timestamp):
		image = osu_d["slider_img"]
		x_pos, y_pos = x_pos - osu_d["x offset"], y_pos - osu_d["y offset"]
		duration = osu_d["duration"] + osu_d["time"] - cur_time
		pixel_length, color = osu_d["pixel length"], osu_d["combo_color"]
	
		# bezier info to calculate curve for sliderball. Actually the first three info is needed for the curve computing
		# function, but we add stack to reduce sliders list size
		b_info = (osu_d["slider type"], osu_d["ps"], osu_d["pixel length"], osu_d["stacking"], osu_d["slider ticks"])
		timestamp = str(timestamp) + "s"
		# [image, x, y, current duration, opacity, color, sliderball index, original duration, bezier info, cur_repeated, repeated, appear followcircle, tick alpha, arrow index]
		self.sliders[timestamp] = [image, x_pos, y_pos, duration, 0, color, self.slidermax_index, osu_d["duration"],
		                           b_info, 1, osu_d["repeated"], 0, [0] * len(osu_d["slider ticks"]), 0]

		pos1 = osu_d["ps"][-1]
		pos2 = osu_d["ps"][-2] # if osu_d["ps"][-2].x != pos1.x or osu_d["ps"][-2].y != pos1.y else osu_d["ps"][-3]

		pos3 = osu_d["ps"][0]
		pos4 = osu_d["ps"][1] # if osu_d["ps"][1].x != pos3.x or osu_d["ps"][1].y != pos3.y else osu_d["ps"][2]

		vector_x1, vector_y1 = pos2.x - pos1.x, pos2.y - pos1.y
		vector_x2, vector_y2 = pos4.x - pos3.x, pos4.y - pos3.y

		angle1 = -np.arctan2(vector_y1, vector_x1) * 180 / np.pi
		angle2 = -np.arctan2(vector_y2, vector_x2) * 180 / np.pi

		img1 = self.reversearrow.rotate_images(angle1)
		img2 = self.reversearrow.rotate_images(angle2)

		self.arrows[timestamp] = [img2, img1]

	def to_frame(self, img, background, x_offset, y_offset, alpha=1):
		# to_3channel done in generate_slider.py
		y1, y2 = y_offset, y_offset + img.shape[0]
		x1, x2 = x_offset, x_offset + img.shape[1]

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])
		if alpha <= 0:
			return
		if alpha < 1:
			tmp = img[ystart:yend, xstart:xend, :] * alpha
		else:
			tmp = img[ystart:yend, xstart:xend, :]

		alpha_l = 1.0 - tmp[:, :, 3]


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

				self.img = self.sliderfollow_fadeout[index]
				super().add_to_frame(background, x, y)

				# frame to make the sliderfollowcircle smaller, but it's smalling too fast so instead of increase index
				# by 1, we increase it by 0.65 then convert it to integer. So some frames would appear twice.
				self.sliders[i][6] = max(0, min(self.slidermax_index, self.sliders[i][6] + self.sliders[i][11]))

				# reduce opacity of slider
				self.sliders[i][4] = max(-self.opacity_interval, self.sliders[i][4] - 4 * self.opacity_interval)


		self.sliders[i][4] = min(100, self.sliders[i][4] + self.opacity_interval)
		cur_img = self.sliders[i][0][:, :, :]
		self.to_frame(cur_img, background, self.sliders[i][1], self.sliders[i][2], alpha=self.sliders[i][4]/100)

		t = self.sliders[i][3] / self.sliders[i][7]

		# if sliderball is going forward
		if going_forward:
			t = 1 - t

		for count, tick_t in enumerate(self.sliders[i][8][4]):
			if self.sliders[i][9] == self.sliders[i][10]:
				if (going_forward and t > tick_t) or (not going_forward and t < tick_t):
						continue

			if self.sliders[i][3] < self.sliders[i][7] + 100:
				if count == 0 or self.sliders[i][12][count-1] >= 0.75:
					self.sliders[i][12][count] = min(1, self.sliders[i][12][count] + 0.1)
			tick_pos = baiser(round(tick_t, 3))
			x = int((tick_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((tick_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown

			self.slidertick.add_to_frame(background, x, y, alpha=self.sliders[i][4] / 100 * self.sliders[i][12][count])



		if 0 < self.sliders[i][3] <= self.sliders[i][7]:
			cur_pos = baiser(round(t, 3))
			x = int((cur_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown
			color = self.sliders[i][5] - 1
			index = int(self.sliders[i][6])

			self.img = self.sliderb_frames[color][index]
			super().add_to_frame(background, x, y)
			self.sliders[i][6] = max(0, min(self.slidermax_index, self.sliders[i][6] + self.sliders[i][11]))

		if self.sliders[i][9] < self.sliders[i][10]:
			cur_pos = baiser(int(going_forward))
			x = int((cur_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown

			self.img = self.arrows[i][int(going_forward)][int(self.sliders[i][13])][:, :, :]
			super().add_to_frame(background, x, y, alpha=self.sliders[i][4] / 100)

			self.sliders[i][13] += 0.6
			if self.sliders[i][13] >= len(self.arrows[i][0]):
				self.sliders[i][13] = 0
