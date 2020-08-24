from osr2mp4.ImageProcess import imageproc

from osr2mp4.ImageProcess.Objects.FrameObject import FrameObject


class Accuracy(FrameObject):
	def __init__(self, frames, gap, settings):
		"""
		:param y: int height of the position. Needs to be right under the score
		:param gap: int
		:param width: int
		:param scale: float
		:param frames: [PIL.Image]
		"""
		super().__init__(frames, settings=settings)
		self.frames = frames[0]

		self.divide_by_255 = 1 / 255.0
		self.width = self.settings.width
		self.total = {300: 0, 100: 0, 50: 0, 0: 0}
		self.maxscore = 0
		self.curscore = 0
		self.gap = gap * 0.5 * self.settings.scale
		self.sizegap = self.gap - self.frames[0].size[0]
		self.y = frames[1] * 0.625 + self.frames[0].size[1] * 0.625 * 0.5 + 3 * self.settings.scale + self.frames[0].size[1]//2
		self.startx = self.settings.width - 18 * self.settings.scale + self.gap//2

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

	def draw_acc(self, acc, background, x):
		"""
		:param acc: string
		:param background: PIL.Image
		:param x: int
		:param y: int
		:return:
		"""
		y = self.y + self.h()/2
		imageproc.add(self.frames["%"], background, x, y)
		x = x + self.gap - self.frames["%"].size[0]

		imageproc.draw_number(background, acc, self.frames, x, y, alpha=1, origin="right", gap=self.gap, constantgap=False)

	def add_to_frame(self, background, inbreak):
		if self.maxscore == 0:
			acc = '100.00'
		else:
			acc = "{:.2f}".format(self.curscore/self.maxscore * 100)

		if self.settings.settings["In-game interface"] or inbreak:
			self.draw_acc(acc, background, self.startx)
