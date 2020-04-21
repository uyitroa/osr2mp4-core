from recordclass import recordclass

from PIL import Image

from Curves.generate_slider import GenerateSlider
from Curves.curve import *

Slider = recordclass("Slider", "image x y cur_duration opacity color sliderb_i orig_duration bezier_info "
                               "cur_repeated repeated appear_f tick_a arrow_i")

class SliderManager:
	def __init__(self, frames, diff, scale, skin, movedown, moveright):
		self.scale = scale
		self.movedown = movedown
		self.moveright = moveright

		self.reversearrow, self.sliderb_frames, self.sliderfollow_fadeout, self.slidertick = frames
		self.slidermax_index = len(self.sliderfollow_fadeout) - 1

		self.divide_by_255 = 1 / 255.0
		self.interval = 1000 / 60

		self.arrows = {}
		self.sliders = {}

		self.cs = (54.4 - 4.48 * diff["CircleSize"])

		self.sliderborder = skin.colours["SliderBorder"]
		self.slideroverride = skin.colours["SliderTrackOverride"]
		self.gs = GenerateSlider(self.sliderborder, self.slideroverride, self.cs, scale)

		self.ar = diff["ApproachRate"]
		self.slidermutiplier = diff["SliderMultiplier"]
		self.calculate_ar()

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

	def add_slider(self, osu_d, x_pos, y_pos, cur_time):
		pixel_length, color = osu_d["pixel length"], osu_d["combo_color"]

		# bezier info to calculate curve for sliderball. Actually the first three info is needed for the curve computing
		# function, but we add stack to reduce sliders list size
		b_info = (osu_d["slider type"], osu_d["ps"], pixel_length, osu_d["stacking"], osu_d["slider ticks"])

		image, x_offset, y_offset = self.gs.get_slider_img(*b_info[0:3])

		pos1 = osu_d["ps"][-1]
		pos2 = osu_d["ps"][-2] if osu_d["ps"][-2].x != pos1.x or osu_d["ps"][-2].y != pos1.y else osu_d["ps"][-3]

		pos3 = osu_d["ps"][0]
		pos4 = osu_d["ps"][1] if osu_d["ps"][1].x != pos3.x or osu_d["ps"][1].y != pos3.y else osu_d["ps"][2]

		vector_x1, vector_y1 = pos2.x - pos1.x, pos2.y - pos1.y
		vector_x2, vector_y2 = pos4.x - pos3.x, pos4.y - pos3.y

		angle1 = -np.arctan2(vector_y1, vector_x1) * 180 / np.pi
		angle2 = -np.arctan2(vector_y2, vector_x2) * 180 / np.pi

		img1 = self.reversearrow.rotate_images(angle1)
		img2 = self.reversearrow.rotate_images(angle2)
		# else:
		# 	x_offset, y_offset = 0, 0
		# 	image = img1 = img2 = np.zeros((1, 1, 4))

		# [image, x, y, current duration, opacity, color, sliderball index, original duration, bezier info,
		# cur_repeated, repeated, appear followcircle, tick alpha, arrow index]
		self.sliders[str(osu_d["time"]) + "s"] = Slider(image, x_pos - x_offset, y_pos - y_offset,
		                                                osu_d["duration"] + osu_d["time"] - cur_time,
		                                                0, color, self.slidermax_index, osu_d["duration"], b_info,
		                                                1,
		                                                osu_d["repeated"], 0, [0] * len(osu_d["slider ticks"]), 0)

		self.arrows[str(osu_d["time"]) + "s"] = [img2, img1]

	def slider_to_frame(self, img, background, x_offset, y_offset, alpha=1):
		a = img
		if 0 < alpha < 1:
			a = img.getchannel("A")
			a = a.point(lambda i: i * alpha)
		if alpha == 0:
			return
		background.paste(img, (x_offset, y_offset), a)

	def sliderstuff_to_frame(self, img, background, x_offset, y_offset, alpha=1):

		a = img
		if 0 < alpha < 1:
			a = img.getchannel("A")
			a = a.point(lambda i: i * alpha)
		if alpha == 0:
			return

		y1 = y_offset - int(img.size[1] / 2)
		x1 = x_offset - int(img.size[0] / 2)
		background.paste(img, (x1, y1), a)

	#
	# def changealpha(self, img, alpha, old_alpha):
	# 	alpha = alpha/old_alpha
	# 	a = img.getchannel('A')
	# 	a = a.point(lambda i: i * alpha)
	# 	img.putalpha(a)

	def add_to_frame(self, background, i, _):
		self.sliders[i].cur_duration -= self.interval
		baiser = Curve.from_kind_and_points(*self.sliders[i].bezier_info[0:3])

		# if sliderball is going forward
		going_forward = self.sliders[i].cur_repeated % 2 == 1

		if self.sliders[i].cur_duration <= 0:
			# if the slider is repeated
			if self.sliders[i].cur_repeated < self.sliders[i].repeated:
				self.sliders[i].cur_duration = self.sliders[i].orig_duration  # reset
				self.sliders[i].cur_repeated += 1
				going_forward = not going_forward

			else:
				cur_pos = baiser(int(going_forward))  # if going_foward is true then t = 1 otherwise it's 0
				x = int((cur_pos.x + self.sliders[i].bezier_info[3]) * self.scale) + self.moveright
				y = int((cur_pos.y + self.sliders[i].bezier_info[3]) * self.scale) + self.movedown

				index = int(self.sliders[i].sliderb_i)

				self.sliderstuff_to_frame(self.sliderfollow_fadeout[index], background, x, y)

				# frame to make the sliderfollowcircle smaller, but it's smalling too fast so instead of increase index
				# by 1, we increase it by 0.65 then convert it to integer. So some frames would appear twice.
				self.sliders[i].sliderb_i = max(0, min(self.slidermax_index,
				                                       self.sliders[i].sliderb_i + self.sliders[i].appear_f))

				# reduce opacity of slider
				self.sliders[i].opacity = max(-self.opacity_interval,
				                              self.sliders[i].opacity - 4 * self.opacity_interval)

		self.sliders[i].opacity = min(90, self.sliders[i].opacity + self.opacity_interval)
		self.slider_to_frame(self.sliders[i].image, background, self.sliders[i].x, self.sliders[i].y, alpha=self.sliders[i].opacity/100)

		t = self.sliders[i].cur_duration / self.sliders[i].orig_duration

		# if sliderball is going forward
		if going_forward:
			t = 1 - t

		for count, tick_t in enumerate(self.sliders[i].bezier_info[4]):
			if self.sliders[i].cur_repeated == self.sliders[i].repeated:
				if (going_forward and t > tick_t) or (not going_forward and t < tick_t):
					continue

			if self.sliders[i].cur_duration < self.sliders[i].orig_duration + 100:
				if count == 0 or self.sliders[i].tick_a[count - 1] >= 0.75:
					self.sliders[i].tick_a[count] = min(1, self.sliders[i].tick_a[count] + 0.1)
			tick_pos = baiser(round(tick_t, 3))
			x = int((tick_pos.x + self.sliders[i].bezier_info[3]) * self.scale) + self.moveright
			y = int((tick_pos.y + self.sliders[i].bezier_info[3]) * self.scale) + self.movedown
			self.slidertick.add_to_frame(background, x, y, alpha=self.sliders[i].opacity * self.sliders[i].tick_a[count]/100)

		if 0 < self.sliders[i].cur_duration <= self.sliders[i].orig_duration:
			cur_pos = baiser(round(t, 3))
			x = int((cur_pos.x + self.sliders[i].bezier_info[3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i].bezier_info[3]) * self.scale) + self.movedown
			color = self.sliders[i].color - 1
			index = int(self.sliders[i].sliderb_i)
			self.sliderstuff_to_frame(self.sliderb_frames[color][index], background, x, y)
			self.sliders[i].sliderb_i = max(0, min(self.slidermax_index,
			                                       self.sliders[i].sliderb_i + self.sliders[i].appear_f))

		if self.sliders[i].cur_repeated < self.sliders[i].repeated:
			cur_pos = baiser(int(going_forward))
			x = int((cur_pos.x + self.sliders[i].bezier_info[3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i].bezier_info[3]) * self.scale) + self.movedown
			self.sliderstuff_to_frame(self.arrows[i][int(going_forward)][int(self.sliders[i].arrow_i)], background, x, y, alpha=self.sliders[i].opacity/100)

			self.sliders[i].arrow_i += 0.6
			if self.sliders[i].arrow_i >= len(self.arrows[i][0]):
				self.sliders[i].arrow_i = 0
