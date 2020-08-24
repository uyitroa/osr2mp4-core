from PIL import Image

from osr2mp4.ImageProcess.Animation.easing import easingout
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.Objects.Components.AScorebar import AScorebar


class Flashlight(AScorebar):
	COMBO_100= 0
	COMBO_200 = 1
	COMBO_BIG = 2
	BREAK = 3

	def __init__(self, frames, settings, hasfl):
		super().__init__(frames, settings=settings)
		self.frame_index = 0
		self.x, self.y = 0, 0
		self.sliding = False
		self.timeframe = self.settings.timeframe/self.settings.fps
		self.hasfl = hasfl
		if self.hasfl:
			self.blackshit = Image.new("RGBA", (settings.width, settings.height), (0, 0, 0, 255))
		else:
			self.blackshit = Image.new("RGBA", (1, 1))

	def set_pos(self, x, y):
		self.x, self.y = x, y

	def update_pos(self, x, y):
		current = self.timeframe
		duration = 120

		self.x = easingout(current, self.x, x - self.x, duration)
		self.y = easingout(current, self.y, y - self.y, duration)

	def set_sliding(self, sliding):
		self.sliding = bool(sliding)

	def set_combo(self, combo):
		if combo >= 200:
			self.frame_index = self.COMBO_BIG
		elif combo >= 100:
			self.frame_index = self.COMBO_200
		else:
			self.frame_index = self.COMBO_100

	def add_to_frame(self, background, inbreak, cursorx, cursory):
		if not self.hasfl:
			return
		AScorebar.animate(self)
		self.update_pos(cursorx, cursory)
		super().add_to_frame(background, self.x, self.y, alpha=self.alpha)
		if inbreak:
			imageproc.add(self.frames[self.BREAK], background, self.x, self.y)
		elif self.sliding:
				imageproc.add(self.blackshit, background, 0, 0, alpha=0.8, topleft=True)
