import numpy
from PIL import Image
from recordclass import recordclass
from ..Components.AScorebar import AScorebar
from ... import imageproc


HitInfo = recordclass("HitInfo", "hitresult delta_t dark")


class URBar(AScorebar):
	def __init__(self, frames, settings):
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

		self.barhitresult = []

		barheight = int(self.h * 0.85)

		self.np = numpy.zeros((barheight, self.w, 4), dtype=numpy.uint8)
		self.np[:, :, 3] = 0
		self.barthin = self.np[0, :, :].copy()
		self.bar_container = Image.frombuffer("RGBA", (self.w, barheight), self.np, 'raw', "RGBA", 0, 1)
		self.bar_container.readonly = False
		self.urbar, self.bar_images, self.maxtime, self.mask = frames

		# (218, 174, 70), (87, 227, 19), (50, 188, 231)

	def add_bar(self, delta_t, hitresult):
		self.barhitresult.append(HitInfo(hitresult, delta_t, 0))

	def add_color(self, delta_t, hitresult, dark):
		pos = int(self.w/2 + delta_t/self.maxtime * self.w/2)
		img = self.bar_images[self.resultdict[hitresult]]
		xstart = max(0, pos-img.shape[0]//2)
		xend = min(self.barthin.shape[0], xstart + img.shape[0])

		imgwidth = xend - xstart
		alpha = 1 - dark/255
		a = self.barthin[xstart:xend, :3] + img[:imgwidth, :3] * alpha
		self.barthin[xstart:xend, 3] = self.barthin[xstart:xend, 3] + dark
		self.barthin[xstart:xend, :3] = a.clip(0, 255)

	def add_to_frame_bar(self, background):
		return
		img = self.urbar
		imageproc.add(img, background, self.x, self.y, alpha=min(1, self.alpha*2))

	def add_to_frame(self, background):
		AScorebar.animate(self)
		self.c += 60/self.settings.fps

		i = len(self.barhitresult)-1
		while i >= 0:
			self.barhitresult[i].dark += 0.3
			if self.barhitresult[i].dark >= 255:
				del self.barhitresult[i]
				i -= 1
				continue
			self.add_color(self.barhitresult[i].delta_t, self.barhitresult[i].hitresult, self.barhitresult[i].dark)
			i -= 1

		self.np[:, :, :] = self.barthin
		self.barthin[:, :] = 0

		s = self.bar_container.size
		self.bar_container.paste((255, 255, 255, 255), (s[0] // 2 - 1, 0, s[0] // 2 + 1, s[1]))

		img = self.urbar.copy()
		imageproc.add(self.bar_container, img, 0, 0, topleft=True, channel=4)
		imageproc.add(img, background, self.x_offset + self.w//2, self.y, alpha=min(1, self.alpha*2))
