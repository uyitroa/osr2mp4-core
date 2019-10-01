from Objects.abstracts import *


class SpinBonusScore(Images):
	def __init__(self, scale, gap, scorenumbers, width, height):
		self.score_frames = []
		self.spinbonuses = ["0", None, None, 10]
		self.score_images = scorenumbers.score_images
		self.gap = int(gap * scale)
		self.divide_by_255 = 1 / 255.0

		self.x = width//2
		self.y = height * 2//3

		self.prepare_scores()


	def prepare_scores(self):
		for image in self.score_images:
			self.score_frames.append([])
			size = 2.5
			for x in range(15, 5, -1):
				buf = ImageBuffer(*image.change_size(size, size))
				super().edit_channel(3, x/15, buf=buf)
				self.score_frames[-1].append(buf)
				size -= 0.1

	def set_bonusscore(self, rotated_bonus):
		if rotated_bonus*1000 == int(self.spinbonuses[0]):
			return
		print(rotated_bonus)
		self.spinbonuses = [str(rotated_bonus*1000), self.x, self.y, 0]

	def xstart(self, n, x, size):
		digits = len(n)
		return int(x - size * (digits-1)/2)

	def add_to_frame(self, background):
		if self.spinbonuses[3] >= 10:
			self.spinbonuses = ["0", None, None, 10]
			return

		index = int(self.spinbonuses[3])
		x = self.xstart(self.spinbonuses[0], self.spinbonuses[1], self.score_frames[0][index].w-self.gap * (2.5 - index/10))
		y = self.spinbonuses[2]

		for digit in self.spinbonuses[0]:
			digit = int(digit)
			self.buf = self.score_frames[digit][index]
			super().add_to_frame(background, x, y)
			x += int(self.score_frames[digit][index].w - self.gap * (2.5 - index/10))

		self.spinbonuses[3] += 0.75
