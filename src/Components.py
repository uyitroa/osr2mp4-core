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
		self.change_size(1, 1)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]
		# self.y1_toreset = None
		# self.y2_toreset = None
		# self.x1_toreset = None
		# self.x2_toreset = None
		# self.to_reset = np.empty((self.img.shape[0], self.img.shape[1], 3))

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

	def add_to_frame(self, background, x_offset, y_offset, overlayalpha=False):
		y1, y2 = y_offset - int(self.img.shape[0]/2), y_offset + int(self.img.shape[0]/2)
		x1, x2 = x_offset - int(self.img.shape[1]/2), x_offset + int(self.img.shape[1]/2)

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])
		alpha_s = self.img[ystart:yend, xstart:xend, 3] / 255.0
		alpha_l = 1.0 - alpha_s

		# self.to_reset[:] = background[y1:y2, x1:x2
		# self.y1_toreset, self.y2_toreset, self.x1_toreset, self.x2_toreset = y1, y2, x1, x2
		for c in range(3):
			background[y1:y2, x1:x2, c] = (alpha_s * self.img[ystart:yend, xstart:xend, c] + alpha_l * background[y1:y2, x1:x2, c])
		if overlayalpha:
			sub = self.img[ystart:xend, xstart:xend, 3] + background[y1:y2, x1:x2, 3]
			sub[sub > 255] = 255
			background[y1:y2, x1:x2, 3] = sub
			
	# def reset_frame(self, background):
	# 	background[self.y1_toreset:self.y2_toreset, self.x1_toreset:self.x2_toreset] = self.to_reset

	def change_size(self, new_row, new_col):
		n_rows = int(new_row * self.orig_rows)
		n_rows -= int(n_rows % 2 == 1)
		n_cols = int(new_col * self.orig_cols)
		n_cols -= int(n_cols % 2 == 1)
		self.img = cv2.resize(self.orig_img, (n_cols, n_rows), interpolation=cv2.INTER_NEAREST)
		self.to_reset = np.empty((self.img.shape[0], self.img.shape[1], 3))


class Cursor(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)


class InputOverlay(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)
		self.cur_blue = 0
		self.size = 1
		self.font_scale = 0.5
		self.font_width, self.font_height = cv2.getTextSize('0', cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
		self.one_digit_size = self.font_width
		self.clicked_called = False
		self.going_down_frame = False
		self.going_up_frame = False
		self.n = '0'
		self.color = (0, 255, 0)

	def addcolor(self, n, color=0):
		self.img[:, :, color] = np.add(self.img[:, :, color], n)

	def clicked(self):
		if not self.going_down_frame:
			self.n = str(int(self.n) + 1)
			self.font_width = self.one_digit_size * len(self.n)
		self.clicked_called = True
		self.going_down_frame = True
		if self.size > 0.9:
			self.size -= 0.02
			self.font_scale -= 0.02
			self.font_width *= self.font_scale/(self.font_scale + 0.02)
			self.font_height *= self.font_scale/(self.font_scale + 0.02)
			self.cur_blue -= 30
			self.change_size(self.size, self.size)
			self.addcolor(self.cur_blue)

	def add_to_frame(self, background, x_offset, y_offset):
		if not self.clicked_called and self.going_down_frame:
			self.going_down_frame = False
			self.already_down = False
			self.going_up_frame = True
		if self.going_up_frame:
			self.size += 0.02
			self.font_scale += 0.02
			self.font_width *= self.font_scale/(self.font_scale - 0.02)
			self.font_height *= self.font_scale/(self.font_scale - 0.02)
			self.cur_blue += 30
			if self.size == 1:
				self.going_up_frame = False
				self.cur_blue = 0
			self.change_size(self.size, self.size)
		center_x = int((self.img.shape[1] - self.font_width) / 2)
		center_y = int((self.font_height + self.img.shape[0])/2)
		cv2.putText(self.img, self.n, (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, self.font_scale, self.color, 2)
		super().add_to_frame(background, x_offset, y_offset)
		self.clicked_called = False


class Cursortrail(Images):
	def __init__(self, filename, cursor_x, cursor_y):
		Images.__init__(self, filename)
		# self.change_size(1, 1)
		# self.orig_img = np.copy(self.img)
		self.trail = [[cursor_x, cursor_y, x] for x in[0.2, 0.32, 0.44, 0.56, 0.68, 0.8, 0.92, 1, 0]]

	def add_to_frame(self, background, x_offset, y_offset):
		self.trail[-1][0], self.trail[-1][1] = x_offset, y_offset
		for x in range(len(self.trail) - 1):
			self.img[:, :, 0:3] = self.orig_img[:, :, 0:3] * self.trail[x][2]
			self.trail[x][0], self.trail[x][1] = self.trail[x + 1][0], self.trail[x + 1][1]
			super().add_to_frame(background, self.trail[x][0], self.trail[x][1])



class Smoke(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)
		self.smokes = [[]]
		self.holding = False

	def clicked(self, cursor_x, cursor_y):
		self.holding = True
		self.smokes[-1].append([cursor_x, cursor_y, 1, 300])

	def add_to_frame(self, background):
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
		self.scale = circle_radius*2/default_circle_size
		self.change_size(self.scale, self.scale)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]


class Number:
	def __init__(self, radius, path, default_circle_size):
		self.combo_number = []
		for x in range(10):
			self.combo_number.append(HitCircleNumber(path + "default-" + str(x) + ".png", radius, default_circle_size))

	def draw(self, circle, number, gap):
		number = str(number)
		size = gap * (len(number) - 1)
		x_pos = int((circle.shape[1]/2) - (size/2))
		y_pos = int(circle.shape[0]/2)

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
		print("done")

	def prepare_sizes(self):
		alpha = 0
		for time_left in range(self.time_preempt, 0, -self.interval):
			alpha = min(100, alpha + self.opacity_interval)
			approach_size = self.cs + (time_left / self.time_preempt) * self.scale * self.cs
			scale = approach_size * 2/self.orig_cols
			self.change_size(scale, scale)
			#self.img[:, :, 3] = self.img[:, :, 3] * (alpha / 100)
			self.approach_frames.append(self.img)


	def add_to_frame(self, background, x_offset, y_offset, time_left):
		self.img = self.approach_frames[int((self.time_preempt - time_left)/self.interval)]
		super().add_to_frame(background, x_offset, y_offset)


class Circles(Images):
	def __init__(self, filename, path, diff, scale, approachfile, maxcombo, gap):
		Images.__init__(self, filename)

		self.diff = diff
		self.circles = []
		self.interval = 1000 / 60  # ms between 2 frames

		ar = diff["ApproachRate"]
		if ar < 5:
			self.time_preempt = 1200 + 600 * (5 - ar) / 5
			fade_in = 800 + 400 * (5 - ar) / 5
		elif ar == 5:
			self.time_preempt = 1200
			fade_in = 800
		else:
			self.time_preempt = 1200 - 750 * (ar - 5) / 5
			fade_in = 800 - 500 * (ar - 5) / 5
		self.opacity_interval = int(fade_in / 100)
		self.cs = (54.4 - 4.48 * diff["CircleSize"]) * scale
		cur_radius = self.orig_cols/2
		radius_scale = self.cs/cur_radius
		default_circle_size = self.orig_rows # save for number class
		self.change_size(radius_scale, radius_scale)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.img.shape[0]
		self.orig_cols = self.img.shape[1]

		self.maxcombo = maxcombo
		self.gap = gap

		self.number_drawer = Number(self.orig_rows/2, path, default_circle_size)
		self.approachCircle = ApproachCircle(approachfile, scale, self.cs, self.time_preempt, self.interval, self.opacity_interval)

		self.circle_frames = []
		self.prepare_circle()

	def add_ar(self, background, x_offset, y_offset):
		y1, y2 = y_offset - int(self.img.shape[0]/2), y_offset + int(self.img.shape[0]/2)
		x1, x2 = x_offset - int(self.img.shape[1]/2), x_offset + int(self.img.shape[1]/2)

		y1, y2, ystart, yend = self.checkOverdisplay(y1, y2, background.shape[0])
		x1, x2, xstart, xend = self.checkOverdisplay(x1, x2, background.shape[1])

		background[y1:y2, x1:x2, :] += self.img[ystart:yend, xstart:xend, :]
		background[y1:y2, x1:x2, :][background[y1:y2, x1:x2, :] > 255] = 255

	def prepare_circle(self):
		for x in range(1, self.maxcombo + 1):
			self.number_drawer.draw(self.img, x, self.gap)
			alpha = 0
			self.circle_frames.append([])
			#self.img[:, :, 3] *= 1.5
			#self.img[:, :, 3][ self.img[:, :, 3] > 255] = 255
			for i in range(len(self.approachCircle.approach_frames)):
				#self.img[:, :, 3] = self.orig_img[:, :, 3] * (alpha/100)
				approach_circle = np.copy(self.approachCircle.approach_frames[i])
				
				x_offset = int(approach_circle.shape[1]/2)
				y_offset = int(approach_circle.shape[0]/2)
				#cv2.imwrite(str(x) + "-" + str(i) + "before.png", self.img)	
				#approach_circle[:, :, 3] = self.img[:, :, 3]
				#super().add_to_frame(approach_circle, x_offset, y_offset, overlayalpha=True)
				self.add_ar(approach_circle, x_offset, y_offset)
				#cv2.imwrite(str(x) + "-" + str(i) + "after.png", approach_circle)
				approach_circle[:, :, 3] = approach_circle[:, :, 3] * (alpha/100)
				self.circle_frames[-1].append(approach_circle)
				alpha = min(100, alpha + self.opacity_interval)
			self.img = np.copy(self.orig_img)
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
				break

			self.img = self.circle_frames[self.circles[i][4] - 1][self.circles[i][3]]
			super().add_to_frame(background, self.circles[i][0], self.circles[i][1])

			i -= 1



if __name__ == "__main__":
	cursor = Cursor("../res/skin/cursor.png")
	print(cursor.img.shape)
