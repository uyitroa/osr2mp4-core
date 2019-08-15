from Curves.generate_slider import GenerateSlider
from Curves.curve import *
import numba


# crop everything that goes outside the screen
@numba.njit(fastmath=True)
def checkOverdisplay(pos1, pos2, limit):
	start = 0
	end = pos2 - pos1

	if pos1 >= limit:
		return 0, 0, 0, 0
	if pos2 <= 0:
		return 0, 0, 0, 0

	if pos1 < 0:
		start = -pos1
		pos1 = 0
	if pos2 >= limit:
		end -= pos2 - limit
		pos2 = limit
	return pos1, pos2, start, end


@numba.njit(fastmath=True)
def to_frame(img, background, x_offset, y_offset):
	# to_3channel done in generate_slider.py
	y1, y2 = y_offset, y_offset + img.shape[0]
	x1, x2 = x_offset, x_offset + img.shape[1]

	y1, y2, ystart, yend = checkOverdisplay(y1, y2, background.shape[0])
	x1, x2, xstart, xend = checkOverdisplay(x1, x2, background.shape[1])
	alpha_s = img[ystart:yend, xstart:xend, 3] * (1/255.0)
	alpha_l = 1.0 - alpha_s

	for c in range(3):
		background[y1:y2, x1:x2, c] = (
				img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])


@numba.njit(fastmath=True)
def to_frame2(img, background, x_offset, y_offset):
	# need to do to_3channel first.
	y1, y2 = y_offset - int(img.shape[0] / 2), y_offset + int(img.shape[0] / 2)
	x1, x2 = x_offset - int(img.shape[1] / 2), x_offset + int(img.shape[1] / 2)

	y1, y2, ystart, yend = checkOverdisplay(y1, y2, background.shape[0])
	x1, x2, xstart, xend = checkOverdisplay(x1, x2, background.shape[1])

	alpha_s = img[ystart:yend, xstart:xend, 3] * (1/255.0)
	alpha_l = 1.0 - alpha_s
	for c in range(3):
		background[y1:y2, x1:x2, c] = (
				img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])


class SliderManager:
	def __init__(self, frames, diff, scale, skin, movedown, moveright):
		self.scale = scale
		self.movedown = movedown
		self.moveright = moveright

		self.reversearrow, self.sliderb_frames, self.sliderfollow_fadeout, self.slidertick = frames
		self.slidermax_index = len(self.sliderfollow_fadeout) - 1

		self.divide_by_255 = 1/255.0
		self.interval = 1000/60

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

		img1 = self.reversearrow.rotate_image(angle1)
		img2 = self.reversearrow.rotate_image(angle2)
		# else:
		# 	x_offset, y_offset = 0, 0
		# 	image = img1 = img2 = np.zeros((1, 1, 4))

		# [image, x, y, current duration, opacity, color, sliderball index, original duration, bezier info,
		# cur_repeated, repeated, appear followcircle, tick alpha]
		self.sliders[str(osu_d["time"]) + "s"] = [image, x_pos - x_offset, y_pos - y_offset,
		                                          osu_d["duration"] + osu_d["time"] - cur_time,
		                                          0, color, self.slidermax_index, osu_d["duration"], b_info, 1,
		                                          osu_d["repeated"], 0, [0] * len(osu_d["slider ticks"])]

		self.arrows[str(osu_d["time"]) + "s"] = [img2, img1]

	# # crop everything that goes outside the screen
	# def checkOverdisplay(self, pos1, pos2, limit):
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
	#
	# def to_frame(self, img, background, x_offset, y_offset):
	# 	# to_3channel done in generate_slider.py
	# 	y1, y2 = y_offset, y_offset + img.shape[0]
	# 	x1, x2 = x_offset, x_offset + img.shape[1]
	#
	# 	y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
	# 	x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])
	# 	alpha_s = img[ystart:yend, xstart:xend, 3] * self.divide_by_255
	# 	alpha_l = 1.0 - alpha_s
	#
	# 	for c in range(3):
	# 		background[y1:y2, x1:x2, c] = (
	# 				img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])
	#
	# def to_frame2(self, img, background, x_offset, y_offset):
	# 	# need to do to_3channel first.
	# 	y1, y2 = y_offset - int(img.shape[0] / 2), y_offset + int(img.shape[0] / 2)
	# 	x1, x2 = x_offset - int(img.shape[1] / 2), x_offset + int(img.shape[1] / 2)
	#
	# 	y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
	# 	x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])
	#
	# 	alpha_s = img[ystart:yend, xstart:xend, 3] * self.divide_by_255
	# 	alpha_l = 1.0 - alpha_s
	# 	for c in range(3):
	# 		background[y1:y2, x1:x2, c] = (
	# 				img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])

	def add_to_frame(self, background, i, _):
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

				to_frame2(self.sliderfollow_fadeout[index], background, x, y)

				# frame to make the sliderfollowcircle smaller, but it's smalling too fast so instead of increase index
				# by 1, we increase it by 0.65 then convert it to integer. So some frames would appear twice.
				self.sliders[i][6] = max(0, min(self.slidermax_index, self.sliders[i][6] + self.sliders[i][11]))

				# reduce opacity of slider
				self.sliders[i][4] = max(-self.opacity_interval, self.sliders[i][4] - 4 * self.opacity_interval)

		self.sliders[i][4] = min(90, self.sliders[i][4] + self.opacity_interval)
		cur_img = self.sliders[i][0][:, :, :] * (self.sliders[i][4] / 100)
		to_frame(cur_img, background, self.sliders[i][1], self.sliders[i][2])

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
			to_frame2(self.sliderb_frames[color][index], background, x, y)
			self.sliders[i][6] = max(0, min(self.slidermax_index, self.sliders[i][6] + self.sliders[i][11]))

		if self.sliders[i][9] < self.sliders[i][10]:
			cur_pos = baiser(int(going_forward))
			x = int((cur_pos.x + self.sliders[i][8][3]) * self.scale) + self.moveright
			y = int((cur_pos.y + self.sliders[i][8][3]) * self.scale) + self.movedown
			arrow_img = self.arrows[i][int(going_forward)][:, :, :] * (self.sliders[i][4] / 100)
			to_frame2(arrow_img, background, x, y)
