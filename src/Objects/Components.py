from Objects.abstracts import *


class Cursor(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)
		self.to_3channel()


class InputOverlay(Images):
	def __init__(self, filename, scale, color):
		Images.__init__(self, filename, scale)
		self.cur_blue = 0
		self.blue_step = 50

		self.frame_index = 0
		self.font_scale = 0.5 * scale
		self.font_step = 0.02
		self.font_width, self.font_height = cv2.getTextSize('0', cv2.FONT_HERSHEY_DUPLEX, self.font_scale, 1)[0]
		self.one_digit_size = self.font_width

		self.clicked_called = False
		self.going_down_frame = False
		self.going_up_frame = False
		self.already_down = False

		self.scale = scale
		self.n = '0'
		self.color = (0, 0, 0)

		self.button_frames = []
		self.to_3channel()
		self.prepare_buttons(color)

	def add_color(self, image, color):
		red = color[0]*self.divide_by_255
		green = color[1]*self.divide_by_255
		blue = color[2]*self.divide_by_255
		image[:, :, 0] = np.multiply(image[:, :, 0], blue, casting='unsafe')
		image[:, :, 1] = np.multiply(image[:, :, 1], green, casting='unsafe')
		image[:, :, 2] = np.multiply(image[:, :, 2], red, casting='unsafe')

	def prepare_buttons(self, color):
		self.button_frames.append(self.img)
		self.change_size(0.97, 0.97)
		self.button_frames.append(self.img)
		for size in range(94, 82, -3):
			self.img = np.copy(self.orig_img)
			size /= 100
			self.change_size(size, size)
			self.add_color(self.img, color)

			self.button_frames.append(self.img)

	def clicked(self):
		is_new_click = not self.going_down_frame
		if not self.going_down_frame:
			self.frame_index = 2
			self.font_scale = 0.5 * self.scale
			self.font_width, self.font_height = cv2.getTextSize('0', cv2.FONT_HERSHEY_DUPLEX, self.font_scale, 1)[0]
			self.n = str(int(self.n) + 1)
			self.font_width = self.one_digit_size * len(self.n)
			self.already_down = False

		self.clicked_called = True
		self.going_down_frame = True
		if self.frame_index < len(self.button_frames) - 1:
			self.frame_index += 1
			self.font_scale -= self.font_step
			self.font_width *= self.font_scale / (self.font_scale + self.font_step)
			self.font_height *= self.font_scale / (self.font_scale + self.font_step)
		return is_new_click

	def add_to_frame(self, background, x_offset, y_offset):
		if self.going_down_frame:
			if not self.already_down:
				self.frame_index += 1
				self.font_scale -= self.font_step
				self.font_width *= self.font_scale / (self.font_scale + self.font_step)
				self.font_height *= self.font_scale / (self.font_scale + self.font_step)

				if self.frame_index >= len(self.button_frames) - 2:
					self.already_down = True

			else:
				if not self.clicked_called:
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
		cv2.putText(background, self.n, (center_x, center_y), cv2.FONT_HERSHEY_DUPLEX, self.font_scale, self.color, 1, lineType=cv2.LINE_AA)
		self.clicked_called = False


class Cursortrail(Images):
	# todo: cursormiddle
	def __init__(self, filename, cursor_x, cursor_y):
		Images.__init__(self, filename)
		self.trail = [[cursor_x, cursor_y] for _ in range(8)]
		self.trail_frames = []
		self.to_3channel()
		self.prepare_trails()

	def prepare_trails(self):
		for x in [0.45, 0.5, 0.6, 0.65, 0.75, 0.9, 1, 0]:
			self.img = np.copy(self.orig_img)
			self.img[:, :, :] = self.orig_img[:, :, :] * x
			self.trail_frames.append(self.img)

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


class InputOverlayBG(Images):
	def __init__(self, filename, scale):
		Images.__init__(self, filename, scale * 1.05)
		self.to_3channel()
		self.orig_img = np.rot90(self.orig_img, 3)
		self.orig_rows = self.orig_img.shape[0]
		self.orig_cols = self.orig_img.shape[1]
		self.img = np.copy(self.orig_img)

	def add_to_frame(self, background, x_offset, y_offset):
		# special y_offset
		y_offset = y_offset + int(self.orig_rows/2)
		super().add_to_frame(background, x_offset, y_offset)
