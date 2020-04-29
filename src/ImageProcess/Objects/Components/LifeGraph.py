import cv2


FORMAT = ".png"


class LifeGraph:
	def __init__(self, filename):
		self.filename = filename + FORMAT
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
		# width = int(self.img.shape[1] * self.cur_life)
		# height = int(self.img.shape[0])
		#
		# background[:height, :width] = self.img[:, :width]
		pass
		#TODO