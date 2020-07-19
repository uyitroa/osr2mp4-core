from .AScorebar import AScorebar


class ScorebarBG(AScorebar):
	def __init__(self, frames, start_time, settings):
		AScorebar.__init__(self, frames, settings=settings)
		self.map_start = start_time

	def add_to_frame(self, background, cur_time, inbreak):
		AScorebar.animate(self)

		if self.settings.settings["In-game interface"] or inbreak:
			# if in break then reset frame will be background's job. Otherwise it's ScorebarBG's job.
			animating = self.h != 0
			if animating or cur_time < self.map_start:
				self.frame_index = 0
				super().add_to_frame(background, 0, -self.h, alpha=self.alpha, topleft=True)
			elif not inbreak:
				background.paste(self.frames[1], (0, -self.h))
