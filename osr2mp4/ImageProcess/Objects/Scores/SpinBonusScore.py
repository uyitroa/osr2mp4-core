from ... import imageproc
from ..FrameObject import FrameObject


class SpinBonusScore(FrameObject):
	def __init__(self, frames, gap, settings):
		super().__init__(frames, settings=settings)
		self.spinbonuses = ["0", None, None, 10]
		self.gap = int(gap * self.settings.scale)

		self.x = self.settings.width//2
		self.y = self.settings.height * 2//3

	def set_bonusscore(self, rotated_bonus):
		if rotated_bonus*1000 == int(self.spinbonuses[0]):
			return
		self.spinbonuses = [str(rotated_bonus*1000), self.x, self.y, 0]

	def xstart(self, n, x, size):
		digits = len(n)
		return int(x - size * (digits-1)/2)

	def draw_score(self, background):
		index = int(self.spinbonuses[3])
		x = self.xstart(self.spinbonuses[0], self.spinbonuses[1], self.frames[0][index].size[0]-self.gap * (2.5 - index/10))
		y = self.spinbonuses[2]
		for digit in self.spinbonuses[0]:
			digit = int(digit)
			img = self.frames[digit][index]
			imageproc.add(img, background, x, y)
			x += int(self.frames[digit][index].size[0] - self.gap * (2.5 - index/10))

	def add_to_frame(self, background):
		if self.spinbonuses[3] >= 10:
			return

		self.draw_score(background)

		self.spinbonuses[3] += 0.75
