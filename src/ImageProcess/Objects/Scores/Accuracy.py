from ..FrameObject import FrameObject
from ....global_var import Settings, GameplaySettings


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
		self.gap = gap * 0.5 * Settings.scale
		self.sizegap = self.gap - self.frames[0].size[0]
		self.y = frames[1] + self.frames[10].size[1]/2  # 67 * Settings.scale
		self.startx = 1347 * Settings.scale + self.gap//2

	def update_acc(self, hitresult):
		self.maxscore += 300
		self.curscore += hitresult
		self.total[hitresult] += 1

	def set_acc(self, total):
		self.total = total
		print(total)
		self.maxscore = 0
		self.curscore = 0
		for x in total:
			self.maxscore += 300 * total[x]
			self.curscore += x * total[x]

	def draw_acc(self, acc, background, x):
		"""
		:param acc: string
		:param background: PIL.Image
		:param x: int
		:param y: int
		:return:
		"""
		self.frame_index = 10  # score_percent
		y = self.y + self.h()/2
		super().add_to_frame(background, x, y)
		x = x + self.gap - self.w()

		for digit in acc[::-1]:
			if digit == '.':
				self.frame_index = 11  # score_dot
			else:
				self.frame_index = int(digit)
			y = self.y + self.h() / 2
			super().add_to_frame(background, x, y)
			x += self.sizegap

	def add_to_frame(self, background, inbreak):
		if self.maxscore == 0:
			acc = '100.00'
		else:
			acc = "{:.2f}".format(self.curscore/self.maxscore * 100)

		if GameplaySettings.settings["In-game interface"] or inbreak:
			self.draw_acc(acc, background, self.startx)
