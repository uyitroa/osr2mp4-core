from ImageProcess.Objects.Components.AScorebar import AScorebar


class ScorebarBG(AScorebar):
	def __init__(self, frames, start_time):
		AScorebar.__init__(self, frames)
		self.map_start = start_time

	def add_to_frame(self, background, cur_time, inbreak):
		AScorebar.animate(self)
		if inbreak or cur_time < self.map_start:
			self.frame_index = 0
		else:
			self.frame_index = 1
		super().add_to_frame(background, 0, -self.h, alpha=self.alpha, topleft=True)
