from Objects.abstracts import *
from PIL import Image

class Cursor(Images):
	def __init__(self, filename, scale):
		Images.__init__(self, filename, scale * 0.75)
		##self.to_3channel()


class Cursortrail(Images):
	# todo: cursormiddle
	def __init__(self, filename, cursor_x, cursor_y, scale):
		Images.__init__(self, filename, scale * 0.75)
		self.trail = [[cursor_x, cursor_y] for _ in range(8)]
		self.trail_frames = []
		#self.to_3channel()
		self.prepare_trails()

	def prepare_trails(self):
		for x in [0.45, 0.5, 0.6, 0.65, 0.75, 0.9, 1, 0]:
			self.img = self.orig_img.copy()
			self.img.putalpha(int(255 * x))
			self.trail_frames.append(self.img)

	def add_to_frame(self, background, x_offset, y_offset):
		# snake algorithm, previous takes the next's one place, etc... the first one takes (x_offset, y_offset) pos.
		self.trail[-1][0], self.trail[-1][1] = x_offset, y_offset
		for x in range(len(self.trail) - 1):
			self.trail[x][0], self.trail[x][1] = self.trail[x + 1][0], self.trail[x + 1][1]
			self.img = self.trail_frames[x]
			super().add_to_frame(background, self.trail[x][0], self.trail[x][1])


class LifeGraph:
	def __init__(self, filename):
		self.filename = filename
		self.img = Image.open(filename)
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
		width = int(self.img.size[1] * self.cur_life)
		height = int(self.img.size[0])

		background[:height, :width] = self.img[:, :width]


class Playfield:
	def __init__(self, filename, width, height):
		self.img = Image.open(filename,)
		self.img.resize(width, height)

	def add_to_frame(self, background):
		y1, y2 = 0, background.size[0]
		x1, x2 = 0, background.size[1]

		alpha_s = self.img[:, :, 3] / 255.0
		alpha_l = 1.0 - alpha_s

		for c in range(0, 3):
			background[y1:y2, x1:x2, c] = (alpha_s * self.img[:, :, c] + alpha_l * background[y1:y2, x1:x2, c])


class TimePie:
	def __init__(self, scale, accuracy):
		# need to initalize this right after initializing accuracy class
		self.scale = scale
		self.y = int(accuracy.y + accuracy.score_images[0].size[0]//2)
		self.x = int(accuracy.width*0.99 - accuracy.score_percent.size[1] - (-accuracy.gap + accuracy.score_images[0].size[1]) * 7)

	def add_to_frame(self, background, cur_time, end_time):
		ratio = cur_time/end_time
		angle = 270
		startangle = -360 + ratio * 360
		endangle = -360
		radius = int(12.5 * self.scale)
		axes = (radius, radius)
		cv2.ellipse(background, (self.x, self.y), axes, angle, startangle, endangle, (125, 125, 125, 255), -1, cv2.LINE_AA)
		cv2.circle(background, (self.x, self.y), radius, (255, 255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
		cv2.circle(background, (self.x, self.y), min(1, int(self.scale)), (255, 255, 255, 255), thickness=-1, lineType=cv2.LINE_AA)
