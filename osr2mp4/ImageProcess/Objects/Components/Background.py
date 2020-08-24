from osr2mp4.ImageProcess.Objects.Components.AScorebar import AScorebar


class Background(AScorebar):
	def __init__(self, bg, start_time, settings, hasfl):
		super().__init__(bg, settings=settings)
		self.map_start = start_time + 50
		self.hasfl = hasfl

	def add_to_frame(self, background, np, cur_time, inbreak):
		AScorebar.animate(self)
		if cur_time <= self.map_start:
			i = max(0, min(1, (self.map_start - cur_time)/1000))
			self.frame_index = round(i * (len(self.frames) - 1))
		else:
			self.frame_index = (1 - self.alpha) * (len(self.frames) - 1)

		# use a more optimised algorithm to draw background and scorebarbg
		if not self.hasfl:
			notanimating = int(self.frame_index) == 0 and self.h == 0
			if notanimating:
				if inbreak or not self.settings.settings["In-game interface"]:
					if self.settings.settings["Background dim"] == 100:
						np.fill(0)
					else:
						# imageproc.add(self.frames[1], background, self.settings.width//2, self.settings.height//2)
						background.paste(self.frames[1], (0, 0))
				return

			self.frame_index = round(self.frame_index)
			super().add_to_frame(background, self.settings.width // 2, self.settings.height // 2)
		else:
			self.frame_index = max(1, round(self.frame_index))
			background.paste(self.frames[int(self.frame_index)])
