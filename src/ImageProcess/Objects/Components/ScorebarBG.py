from ImageProcess.Objects.Components.AScorebar import AScorebar


class ScorebarBG(AScorebar):
	def __init__(self, frames):
		AScorebar.__init__(self, frames)

	def add_to_frame(self, background, inbreak):
		AScorebar.animate(self)
		# if inbreak:
		# 	self.frame_index = 0
		# else:
		# 	self.frame_index = 1
		super().add_to_frame(background, 0, -self.h, alpha=self.alpha, topleft=True)
