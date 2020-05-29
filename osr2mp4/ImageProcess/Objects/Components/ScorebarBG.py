from .AScorebar import AScorebar
from ....global_var import GameplaySettings


class ScorebarBG(AScorebar):
	def __init__(self, frames, start_time):
		AScorebar.__init__(self, frames)
		self.map_start = start_time

	def add_to_frame(self, background, cur_time, inbreak):
		AScorebar.animate(self)
		# if inbreak or cur_time < self.map_start:
		# 	self.frame_index = 0
		# 	h = -self.h
		# else:
		# 	self.frame_index = 1
		# 	h = 0

		if GameplaySettings.settings["In-game interface"] or inbreak:
			if inbreak or cur_time < self.map_start or not (not self.scrolling and self.interval == 0):
				self.frame_index = 0
				super().add_to_frame(background, 0, -self.h, alpha=self.alpha, topleft=True)
			else:
				background.paste(self.frames[1], (0, -self.h))
