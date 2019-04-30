import cv2
import numpy as np
import sys

np.set_printoptions(threshold=sys.maxsize)


class Images:
	def __init__(self, filename):
		self.filename = filename
		self.img = cv2.imread(self.filename, -1)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]
		self.change_size(1, 1) # make rows and cols even amount
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]

	def to_3channel(self):
		alpha_s = self.orig_img[:, :, 3] / 255.0
		for c in range(3):
			self.orig_img[:, :, c] = (self.orig_img[:, :, c] * alpha_s).astype(self.orig_img.dtype)
		self.img = self.orig_img

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

	def add_to_frame(self, background, x_offset, y_offset):
		# need to do to_3channel first.
		y1, y2 = y_offset - int(self.img.shape[0] / 2), y_offset + int(self.img.shape[0] / 2)
		x1, x2 = x_offset - int(self.img.shape[1] / 2), x_offset + int(self.img.shape[1] / 2)

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])
		alpha_s = self.img[ystart:yend, xstart:xend, 3] / 255.0
		alpha_l = 1.0 - alpha_s

		for c in range(3):
			background[y1:y2, x1:x2, c] = (
					self.img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])

	def change_size(self, new_row, new_col, inter_type=cv2.INTER_AREA):
		n_rows = int(new_row * self.orig_rows)
		n_rows -= int(n_rows % 2 == 1)  # need to be even
		n_cols = int(new_col * self.orig_cols)
		n_cols -= int(n_cols % 2 == 1)  # need to be even
		self.img = cv2.resize(self.orig_img, (n_cols, n_rows), interpolation=inter_type)
		self.to_reset = np.empty((self.img.shape[0], self.img.shape[1], 3))


class Cursor(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)
		self.to_3channel()


class InputOverlay(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)

		self.cur_blue = 0
		self.blue_step = 35

		self.frame_index = 0
		self.font_scale = 0.5
		self.font_step = 0.02
		self.font_width, self.font_height = cv2.getTextSize('0', cv2.FONT_HERSHEY_DUPLEX, self.font_scale, 1)[0]
		self.one_digit_size = self.font_width

		self.clicked_called = False
		self.going_down_frame = False
		self.going_up_frame = False

		self.n = '0'
		self.color = (0, 0, 0)

		self.button_frames = []
		self.to_3channel()
		self.prepare_buttons()

	def addcolor(self, n, color=0):
		self.img[:, :, color] = self.img[:, :, color] + n * self.img[:, :, 3]

	def prepare_buttons(self):
		blue = 0
		for size in range(100, 90, -2):
			size /= 100
			self.change_size(size, size)
			self.addcolor(blue)

			self.button_frames.append(self.img)
			blue -= self.blue_step

	def clicked(self):
		if not self.going_down_frame:
			self.n = str(int(self.n) + 1)
			self.font_width = self.one_digit_size * len(self.n)
		self.clicked_called = True
		self.going_down_frame = True
		if self.frame_index < len(self.button_frames) - 1:
			self.frame_index += 1
			self.font_scale -= self.font_step
			self.font_width *= self.font_scale / (self.font_scale + self.font_step)
			self.font_height *= self.font_scale / (self.font_scale + self.font_step)

	def add_to_frame(self, background, x_offset, y_offset):
		if not self.clicked_called and self.going_down_frame:
			self.going_down_frame = False
			self.already_down = False
			self.going_up_frame = True
		if self.going_up_frame:
			self.frame_index -= 1
			self.font_scale += self.font_step
			self.font_width *= self.font_scale / (self.font_scale - self.font_step)
			self.font_height *= self.font_scale / (self.font_scale - self.font_step)
			if self.frame_index == 0:
				self.going_up_frame = False
				self.cur_blue = 0

		self.img = self.button_frames[self.frame_index]
		super().add_to_frame(background, x_offset, y_offset)
		center_x = int(x_offset - self.font_width / 2)
		center_y = int(self.font_height / 2 + y_offset)
		cv2.putText(background, self.n, (center_x, center_y), cv2.FONT_HERSHEY_DUPLEX, self.font_scale, self.color, 1)
		self.clicked_called = False


class Cursortrail(Images):
	def __init__(self, filename, cursor_x, cursor_y):
		Images.__init__(self, filename)
		self.trail = [[cursor_x, cursor_y] for _ in range(8)]
		self.trail_frames = []
		self.to_3channel()
		self.prepare_trails()

	def prepare_trails(self):
		for x in [0.8, 0.82, 0.85, 0.89, 0.94, 0.99, 1, 0]:
			self.img[:, :, 0:3] = self.orig_img[:, :, 0:3] * x
			self.trail_frames.append(self.img)
			self.img = np.copy(self.orig_img)

	def add_to_frame(self, background, x_offset, y_offset):
		# snake algorithm, previous takes the next's one place, etc... the first one takes (x_offset, y_offset) pos.
		self.trail[-1][0], self.trail[-1][1] = x_offset, y_offset
		for x in range(len(self.trail) - 1):
			self.trail[x][0], self.trail[x][1] = self.trail[x + 1][0], self.trail[x + 1][1]
			self.img = self.trail_frames[x]
			super().add_to_frame(background, self.trail[x][0], self.trail[x][1])


class Smoke(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)
		self.smokes = [[]]
		self.holding = False

		self.to_3channel()

	def clicked(self, cursor_x, cursor_y):
		self.holding = True
		self.smokes[-1].append([cursor_x, cursor_y, 1, 300])

	def add_to_frame(self, background):
		# todo: optimize this
		x = 0
		while x < len(self.smokes):
			y = 0
			while y < len(self.smokes[x]):
				self.img[:, :, 0:3] = self.orig_img[:, :, 0:3] * self.smokes[x][y][2]
				super().add_to_frame(background, self.smokes[x][y][0], self.smokes[x][y][1])
				if self.smokes[x][y][3] <= 0:
					self.smokes[x][y][2] -= 0.025
					if self.smokes[x][y][2] <= 0:
						del self.smokes[x][y]
						y -= 1
						if not self.smokes[x]:
							del self.smokes[x]
							x -= 1
							if len(self.smokes) == 1:
								break
				if not self.holding or x < len(self.smokes):
					self.smokes[x][y][3] -= 1
				y += 1
			x += 1
		if not self.holding and self.smokes[-1]:
			self.smokes.append([])
		self.holding = False


class LifeGraph:
	def __init__(self, filename):
		self.filename = filename
		self.img = cv2.imread(filename)
		self.cur_life = 1
		self.to_life = 1
		self.speed = 0
		self.wait_to_goes_down = 90
		self.changing = False

	def goes_to(self, life):
		# self.to_life = life
		# self.changing = True
		# if self.to_life > self.cur_life: # goes up
		# 	self.speed = (self.cur_life - self.to_life) / 120
		# 	self.wait_to_goes_down = 0
		# else:
		# 	self.speed = (self.cur_life - self.to_life) / 20
		# 	self.wait_to_goes_down = 100
		self.cur_life = life

	def add_to_frame(self, background):
		# if self.changing and self.wait_to_goes_down == 0:
		# 	self.wait_to_goes_down = 1
		# 	self.cur_life -= self.speed
		# 	if self.cur_life == self.to_life:
		# 		self.changing = False
		# 	if self.cur_life > 1:
		# 		self.cur_life = 1
		# self.wait_to_goes_down -= 1
		width = int(self.img.shape[1] * self.cur_life)
		height = int(self.img.shape[0])

		background[:height, :width] = self.img[:, :width]
#
# alpha_s = self.img[:, :width, 3] / 255.0
# alpha_l = 1.0 - alpha_s

# self.to_reset[:] = background[y1:y2, x1:x2]
# self.y1_toreset, self.y2_toreset, self.x1_toreset, self.x2_toreset = y1, y2, x1, x2
# for c in range(0, 3):
# 	background[y1:y2, x1:x2, c] = (alpha_s * self.img[:, :width, c] + alpha_l * background[y1:y2, x1:x2, c])


class Playfield:
	def __init__(self, filename, width, height):
		self.img = cv2.imread(filename, -1)
		self.img = cv2.resize(self.img, (width, height), interpolation=cv2.INTER_NEAREST)

	def add_to_frame(self, background):
		y1, y2 = 0, background.shape[0]
		x1, x2 = 0, background.shape[1]

		alpha_s = self.img[:, :, 3] / 255.0
		alpha_l = 1.0 - alpha_s

		for c in range(0, 3):
			background[y1:y2, x1:x2, c] = (alpha_s * self.img[:, :, c] + alpha_l * background[y1:y2, x1:x2, c])


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
			self.combo_number[int(digit)].add_to_frame(circle, x_pos, y_pos)
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


class Circles(Images):
	def __init__(self, filename, overlay_filename, path, diff, scale, approachfile, maxcombo, gap):
		"""
		:param filename: str hitcircle file
		:param overlay_filename: strcircle overlay file
		:param path: str where is the skin folder
		:param diff: dict, contains ApproachRate, CircleSize, OverallDifficulty, HPDrain
		:param scale: float scale of current screen res with 512x384
		:param approachfile: str approach circle file
		:param maxcombo: int, biggest number we need to overlap, for preparing_circle, where we overlap every number with every circle
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

		self.maxcombo = maxcombo
		self.gap = gap

		self.number_drawer = Number(self.orig_rows / 2, path, self.default_circle_size)
		self.approachCircle = ApproachCircle(approachfile, scale, self.cs, self.time_preempt, self.interval,
		                                     self.opacity_interval)

		self.circle_frames = []
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

	def add_color(self):
		red = 255.0/255.0
		green = 0.0/255.0
		blue = 0.0/255.0
		self.img[:, :, 0] = np.multiply(self.img[:, :, 0], blue, casting='unsafe')
		self.img[:, :, 1] = np.multiply(self.img[:, :, 1], green, casting='unsafe')
		self.img[:, :, 2] = np.multiply(self.img[:, :, 2], red, casting='unsafe')
		self.img[self.img > 255] = 255

	def load_circle(self):
		self.overlay = CircleOverlay(self.overlay_filename)
		self.add_color()
		self.overlayhitcircle(self.img, int(self.overlay.orig_cols / 2), int(self.overlay.orig_rows / 2), self.overlay.img)
		self.orig_img = self.img

		cur_radius = self.orig_cols / 2
		self.radius_scale = self.cs / cur_radius
		self.default_circle_size = self.orig_rows  # save for number class
		self.change_size(self.radius_scale * 1.13, self.radius_scale * 1.13, inter_type=cv2.INTER_LINEAR)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]
		self.img = np.copy(self.orig_img)

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

	def overlay_approach(self, background, x_offset, y_offset):
		# still ned 4 channels so cannot do to_3channel before.
		y1, y2 = y_offset - int(self.img.shape[0] / 2), y_offset + int(self.img.shape[0] / 2)
		x1, x2 = x_offset - int(self.img.shape[1] / 2), x_offset + int(self.img.shape[1] / 2)

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])

		alpha_s = background[y1:y2, x1:x2, 3] / 255.0
		alpha_l = 1 - alpha_s
		for c in range(4):
			background[y1:y2, x1:x2, c] = self.img[ystart:yend, xstart:xend, c] * alpha_l + \
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
		for x in range(1, self.maxcombo + 1):
			self.number_drawer.draw(self.img, x, self.gap)
			alpha = 0
			self.circle_frames.append([])
			for i in range(len(self.approachCircle.approach_frames)):
				approach_circle = np.copy(self.approachCircle.approach_frames[i])

				x_offset = int(approach_circle.shape[1] / 2)
				y_offset = int(approach_circle.shape[0] / 2)
				self.overlay_approach(approach_circle, x_offset, y_offset)
				self.to_3channel(approach_circle)
				approach_circle[:, :, 0:3] = approach_circle[:, :, 0:3] * (alpha / 100)

				self.circle_frames[-1].append(approach_circle)
				alpha = min(100, alpha + self.opacity_interval)

			self.img = np.copy(self.orig_img)
		print("done")
		del self.approachCircle

	def add_circle(self, x, y, combo_number):
		self.circles.append([x, y, self.time_preempt, -1, combo_number])

	def add_to_frame(self, background):
		i = len(self.circles) - 1
		while i > -1:
			self.circles[i][2] -= self.interval
			self.circles[i][3] += 1
			if self.circles[i][2] <= 0:
				del self.circles[i]
				break  # break right after since self.circles[i][2] < 0 means i reached 0 so no need to continue the loop

			self.img = self.circle_frames[self.circles[i][4] - 1][self.circles[i][3]]
			super().add_to_frame(background, self.circles[i][0], self.circles[i][1])

			i -= 1


if __name__ == "__main__":
	cursor = Cursor("../res/skin/cursor.png")
	print(cursor.img.shape)
