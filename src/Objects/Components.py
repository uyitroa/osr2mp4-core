from Objects.abstracts import *
import os.path

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
	def __init__(self, filename):
		Images.__init__(self, filename)
		self.to_3channel()
		self.orig_img = np.rot90(self.orig_img, 3)
		self.orig_rows = self.orig_img.shape[0]
		self.orig_cols = self.orig_img.shape[1]
		self.img = np.copy(self.orig_img)


class Fp(Images):
	def __init__(self, filename, scale):
		Images.__init__(self, filename)
		self.to_square()
		self.change_size(scale * 0.5, scale * 0.5)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.orig_img.shape[0]
		self.orig_cols = self.orig_img.shape[1]
		self.to_3channel()

	def to_square(self):
		max_length = int(np.sqrt(self.img.shape[0]**2 + self.img.shape[1]**2) + 2)  # round but with int
		square = np.zeros((max_length, max_length, self.img.shape[2]))
		y1, y2 = int(max_length / 2 - self.orig_rows / 2), int(max_length / 2 + self.orig_rows / 2)
		x1, x2 = int(max_length / 2 - self.orig_cols / 2), int(max_length / 2 + self.orig_cols / 2)
		square[y1:y2, x1:x2, :] = self.img[:, :, :]
		self.orig_img = square
		self.orig_rows, self.orig_cols = max_length, max_length
		# cv2.imwrite("test.png", self.orig_img)
		# cv2.yes

	def rotate_image(self, angle):
		image_center = tuple(np.array(self.img.shape[1::-1]) / 2)
		rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
		result = cv2.warpAffine(self.img, rot_mat, self.img.shape[1::-1], flags=cv2.INTER_LINEAR)
		return result


class FollowPointsManager(Images):
	def __init__(self, filename, scale, movedown, moveright):
		self.fp_frames = []
		self.followpoints = []
		self.pointdistance = 32
		self.scale = scale
		self.movedown = movedown
		self.moveright = moveright
		self.preempt = 800
		self.divide_by_255 = 1/255.0
		counter = 0
		should_continue = True
		fp = None
		while should_continue:
			self.fp_frames.append(fp)
			fp = Fp(filename + "-" + str(counter) + ".png", scale)
			counter += 1
			should_continue = os.path.isfile(filename + "-" + str(counter) + ".png")
		self.fp_frames.pop(0)
		self.img = np.zeros(self.fp_frames[0].orig_img.shape)

	def add_fp(self, x1, y1, t1, next_object):
		x2, y2, t2 = next_object["x"], next_object["y"], next_object["time"]

		spacing = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
		if spacing - self.pointdistance < self.pointdistance * 1.5:  # basically if spacing < 81
			return
		x_vector, y_vector = x2 - x1, y2 - y1
		# x_horizontal, y_horizontal = 1, 0
		# angle = np.rad2deg(np.arccos((x_vector*x_horizontal + y_horizontal*y_vector)/spacing))  # dot product
		# if y_vector >= 0:
		# 	angle *= -1
		angle = -np.arctan2(y_vector, x_vector) * 180 / np.pi
		self.followpoints.append([[], x1, y1, x_vector, y_vector, t1, t2, int(spacing)])

		for x in range(len(self.fp_frames)):
			self.followpoints[-1][0].append(self.fp_frames[x].rotate_image(angle))

	def add_to_frame(self, background, cur_time):
		i = len(self.followpoints) - 1
		alpha_tdelta = 200
		while i > -1:
			d = self.pointdistance * 1.5
			duration = self.followpoints[i][6] - self.followpoints[i][5]
			to_delete = False
			while d < self.followpoints[i][7] - self.pointdistance:
				fraction = d/self.followpoints[i][7]
				fadeouttime = self.followpoints[i][5] + fraction * duration + alpha_tdelta
				fadeintime = fadeouttime - self.preempt

				if cur_time < fadeintime:
					break
				if cur_time > fadeouttime:
					d += self.pointdistance
					to_delete = d >= self.followpoints[i][7] - self.pointdistance
					continue


				x = self.followpoints[i][1] + fraction * self.followpoints[i][3]
				x = int(x * self.scale) + self.moveright
				y = self.followpoints[i][2] + fraction * self.followpoints[i][4]
				y = int(y * self.scale) + self.movedown

				# quick maths
				alpha = min(1, (cur_time - fadeintime)/alpha_tdelta, (fadeouttime - cur_time)/alpha_tdelta)

				total_time = fadeouttime - fadeintime
				cur_time_gone = cur_time - fadeintime
				index = int(cur_time_gone * (len(self.followpoints[i][0]))/total_time)
				if index >= len(self.followpoints[i][0]):
					index -= len(self.followpoints[i][0])

				self.img = self.followpoints[i][0][index][:, :, :] * alpha
				super().add_to_frame(background, x, y)
				d += self.pointdistance
			if to_delete:
				del self.followpoints[i]
				break
			i -= 1
