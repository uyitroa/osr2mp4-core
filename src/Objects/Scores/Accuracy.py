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
		self.total = {300: 0, 100: 0, 50: 0, 0: 0}
		self.maxscore = 0
		self.curscore = 0
		self.gap = int(gap * scale * 0.5)
		self.y = int(self.scorenumbers.score_images[0].img.size[1] * 0.75)
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
		self.total[hitresult] += 1

	def set_acc(self, total):
		self.total = total
		self.maxscore = 0
		self.curscore = 0
		for x in total:
			self.maxscore += 300 * total[x]
			self.curscore += x * total[x]

	def add_to_frame(self, background):
		if self.maxscore == 0:
			acc = '100.00'
		else:
			acc = "{:.2f}".format(self.curscore/self.maxscore * 100)
		startx = int(self.width * 0.99)

		self.img = self.score_percent
		x, y = startx - self.img.size[0]//2, self.y + self.img.size[1]//2
		super().add_to_frame(background, x, y)

		numberwidth = int(self.score_images[0].size[0])
		x = startx - self.img.size[0] - (-self.gap + numberwidth) * (len(acc)-1)
		y = self.y + self.score_images[0].size[1]//2
		for digit in acc:
			if digit == '.':
				self.img = self.score_dot
				super().add_to_frame(background, x-self.img.size[0]+self.gap, y)
				x += self.img.size[0] - self.gap
				continue
			self.img = self.score_images[int(digit)]
			super().add_to_frame(background, x, y)
			x += -self.gap + numberwidth
