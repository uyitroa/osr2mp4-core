import numpy
from PIL import Image

from osr2mp4.ImageProcess.Animation.easing import easingout
from osr2mp4.ImageProcess.Objects.Components.AScorebar import AScorebar
from osr2mp4.ImageProcess import imageproc


class URBar(AScorebar):
	def __init__(self, frames, urarrow, settings):
		AScorebar.__init__(self, frames[0], settings=settings)
		self.scale = settings.scale
		self.settings = settings
		self.w, self.h = int(frames[0].size[0]), int(frames[0].size[1])
		self.y = settings.height - self.h//2
		self.x = settings.width//2

		self.x_offset = self.x - self.w // 2

		self.bars = []
		self.resultdict = {50: 0, 100: 1, 300: 2}

		self.c = 0

		barheight = int(self.h * 0.8)

		self.np = numpy.zeros((barheight, self.w, 4), dtype=numpy.uint8)
		self.np[:, :, 3] = 0
		self.barthin = self.np[0, :, :].copy()
		self.bar_container = Image.frombuffer("RGBA", (self.w, barheight), self.np, 'raw', "RGBA", 0, 1)
		self.bar_container.readonly = False
		self.urbar, self.bar_images, self.maxtime, self.mask = frames

		self.floatingerror = self.w/2
		self.arrowx = self.w/2
		self.urarrow = urarrow[0]
		self.arrowy = self.h // 4

	def add_bar(self, delta_t, hitresult):
		pos = self.w/2 + delta_t/self.maxtime * self.w/2

		self.floatingerror = self.floatingerror * 0.8 + pos * 0.2

		pos = int(pos)
		img = self.bar_images[self.resultdict[hitresult]]
		xstart = max(0, pos-img.shape[0]//2)
		xend = min(self.barthin.shape[0], xstart + img.shape[0])

		imgwidth = xend - xstart

		a = self.barthin[xstart:xend, :] + img[:imgwidth, :]
		self.barthin[xstart:xend, :] = a.clip(0, 255)

	def add_to_frame_bar(self, background):
		if not self.settings.settings["Show score meter"]:
			return
		img = self.urbar
		imageproc.add(img, background, self.x, self.y, alpha=min(1, self.alpha*2))

	def movearrow(self, current=None):
		current = self.settings.timeframe/self.settings.fps
		change = self.floatingerror - self.arrowx
		duration = 800
		self.arrowx = easingout(current, self.arrowx, change, duration)

	def add_to_frame(self, background):
		if not self.settings.settings["Show score meter"]:
			return
		AScorebar.animate(self)

		self.c += 60/self.settings.fps
		self.np[:, :, :] = self.barthin

		s = self.bar_container.size
		self.bar_container.paste((255, 255, 255, 255), (s[0] // 2 - 1, 0, s[0] // 2 + 1, s[1]))

		img = self.bar_container
		imageproc.add(img, background, self.x_offset + self.w//2, self.y, alpha=min(1, self.alpha*2))

		if self.c >= 6:
			a = self.barthin[:, :] - self.mask
			self.barthin[:, :] = a.clip(0, 255)
			self.c = 0

		self.movearrow()
		imageproc.add(self.urarrow, background, self.x_offset + self.arrowx, self.y-self.arrowy, alpha=min(1, self.alpha*2))
