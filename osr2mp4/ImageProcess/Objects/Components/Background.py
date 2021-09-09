from osr2mp4.ImageProcess.Objects.Components.AScorebar import AScorebar


class Background(AScorebar):
	def __init__(self, bg, start_time, settings, hasfl):
		super().__init__(bg, settings=settings)
		self.map_start: int = start_time + 50
		self.hasfl: int = hasfl
		self.bg_alpha: int = 0

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
			
			"""
			if self.settings.settings['Dont change dim levels during breaks']:
				return np.fill(0)
			"""

			if notanimating:
				if inbreak or not self.settings.settings["In-game interface"]:
					if self.settings.settings["Background dim"] == 100:
						np.fill(0)
				else:
					if self.settings.settings['Show background video']:
						np.fill(0) # this is for 4:3 resolution when the background video height is smaller than the main height
								   # it looks kinda gay with the bg bein visible so i disable it :troll:
					else:
						background.paste(self.frames[1], (0, 0))
				return

			self.frame_index = round(self.frame_index)

			super().add_to_frame(background, self.settings.width // 2, self.settings.height // 2)
		else:
			self.frame_index = max(1, round(self.frame_index))

			if self.settings.settings['Show background video']:
				np.fill(0)
			else:
				background.paste(self.frames[int(self.frame_index)])