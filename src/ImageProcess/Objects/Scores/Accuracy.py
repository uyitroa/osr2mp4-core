from ImageProcess.Objects.FrameObject import FrameObject
from global_var import Settings


class Accuracy(FrameObject):
	def __init__(self, frames, gap):
		"""
		:param y: int height of the position. Needs to be right under the score
		:param gap: int
		:param width: int
		:param scale: float
		:param frames: [PIL.Image]
		"""
		super().__init__(frames)
		self.frames = frames[0]

		self.divide_by_255 = 1 / 255.0
		self.width = Settings.width
		self.total = {300: 0, 100: 0, 50: 0, 0: 0}
		self.maxscore = 0
		self.curscore = 0
		self.gap = int(gap * Settings.scale * 0.5)
		self.y = frames[1]

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

	def draw_acc(self, acc, background, x, y):
		"""
		:param acc: string
		:param background: PIL.Image
		:param x: int
		:param y: int
		:return:
		"""
		numberwidth = int(self.frames[0].size[0])
		for digit in acc:
			if digit == '.':
				self.frame_index = 11  # score_dot
				super().add_to_frame(background, x-self.w()+self.gap, y)
				x += self.w() - self.gap
				continue

			self.frame_index = int(digit)
			super().add_to_frame(background, x, y)
			x += -self.gap + numberwidth

	def add_to_frame(self, background):
		if self.maxscore == 0:
			acc = '100.00'
		else:
			acc = "{:.2f}".format(self.curscore/self.maxscore * 100)
		startx = int(self.width * 0.99)

		self.frame_index = 10  # score_percent
		x, y = startx - self.w()//2, self.y + self.h()//2
		super().add_to_frame(background, x, y)

		numberwidth = int(self.frames[0].size[0])
		x = startx - self.w() - (-self.gap + numberwidth) * (len(acc)-1)
		y = self.y + self.frames[0].size[1]//2
		self.draw_acc(acc, background, x, y)
