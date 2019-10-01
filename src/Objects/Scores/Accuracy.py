from Objects.abstracts import *


class Accuracy(Images):
	def __init__(self, scorenumbers, width, height, gap, scale):
		self.scorenumbers = scorenumbers
		self.score_images = [None] * 10
		self.score_percent = None
		self.score_dot = None
		self.width = width
		self.height = height
		self.total = {300:0, 100: 0, 50: 0, 0: 0}
		self.maxscore = 0
		self.curscore = 0
		self.gap = int(gap * scale * 0.5)
		self.y = int(self.scorenumbers.score_images[0].buf.h * 0.75)
		self.prepare_numbers()

	def prepare_numbers(self):
		for index, img in enumerate(self.scorenumbers.score_images):
			buf = ImageBuffer(*img.change_size(0.5, 0.5))
			self.score_images[index] = buf
		self.score_percent = ImageBuffer(*self.scorenumbers.score_percent.change_size(0.6, 0.6))

		self.score_dot = ImageBuffer(*self.scorenumbers.score_dot.change_size(0.5, 0.5))

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

		self.buf = self.score_percent
		x, y = startx - self.buf.w//2, self.y + self.buf.h//2
		super().add_to_frame(background, x, y)

		numberwidth = int(self.score_images[0].w)
		x = startx - self.buf.w - (-self.gap + numberwidth) * (len(acc)-1)
		y = self.y + self.score_images[0].h//2
		for digit in acc:
			if digit == '.':
				self.buf = self.score_dot
				super().add_to_frame(background, x-self.buf.w+self.gap, y)
				x += self.buf.w - self.gap
				continue
			self.img = self.score_images[int(digit)]
			super().add_to_frame(background, x, y)
			x += -self.gap + numberwidth
