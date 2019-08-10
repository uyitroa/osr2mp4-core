from Objects.abstracts import *


class Accuracy(Images):
	def __init__(self, scorenumbers, width, height, gap, scale):
		self.divide_by_255 = 1 / 255.0
		self.scorenumbers = scorenumbers
		self.score_images = [None] * 10
		self.score_percent = None
		self.score_dot = None
		self.width = width
		self.height = height
		self.maxscore = 0
		self.curscore = 0
		self.gap = int(gap * scale * 0.5)
		self.y = int(self.scorenumbers.score_images[0].img.shape[0] * 0.75)
		self.prepare_numbers()

	def prepare_numbers(self):
		for index, img in enumerate(self.scorenumbers.score_images):
			img.change_size(0.5, 0.5)
			self.score_images[index] = img.img
		self.scorenumbers.score_percent.change_size(0.6, 0.6)
		self.score_percent = self.scorenumbers.score_percent.img

		self.scorenumbers.score_dot.change_size(0.5, 0.5)
		self.score_dot = self.scorenumbers.score_dot.img

	def update_acc(self, hitresult):
		self.maxscore += 300
		self.curscore += hitresult

	def add_to_frame(self, background):
		if self.maxscore == 0:
			acc = '100.00'
		else:
			acc = "{:.2f}".format(self.curscore/self.maxscore * 100)
		startx = int(self.width * 0.99)

		self.img = self.score_percent
		x, y = startx - self.img.shape[1]//2, self.y + self.img.shape[0]//2
		super().add_to_frame(background, x, y)

		numberwidth = int(self.score_images[0].shape[1])
		x = startx - self.img.shape[1] - (-self.gap + numberwidth) * (len(acc)-1)
		y = self.y + self.score_images[0].shape[0]//2
		for digit in acc:
			if digit == '.':
				self.img = self.score_dot
				super().add_to_frame(background, x-self.img.shape[1]+self.gap, y)
				x += self.img.shape[1] - self.gap
				continue
			self.img = self.score_images[int(digit)]
			super().add_to_frame(background, x, y)
			x += -self.gap + numberwidth
