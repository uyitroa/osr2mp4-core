from .AScorebar import AScorebar


class Background(AScorebar):
	def __init__(self, bg, start_time, settings):
		super().__init__(bg, settings=settings)
		self.map_start = start_time + 50

	def add_to_frame(self, background, np, cur_time, inbreak):
		AScorebar.animate(self)
		if cur_time <= self.map_start:
			i = max(0, min(1, (self.map_start - cur_time)/1000))
			self.frame_index = round(i * (len(self.frames) - 1))
		else:
			self.frame_index = (1 - self.alpha) * (len(self.frames) - 1)

		notanimating = int(self.frame_index) == 0
		if notanimating:
			if inbreak or not self.settings.settings["In-game interface"]:
				if self.settings.settings["Background dim"] == 100:
					np.fill(0)
				else:
					# imageproc.add(self.frames[1], background, self.settings.width//2, self.settings.height//2)
					background.paste(self.frames[1], (0, 0))
			return

		super().add_to_frame(background, self.settings.width//2, self.settings.height//2)
