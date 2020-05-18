from ImageProcess.Objects.Components.AScorebar import AScorebar


class ScorebarBG(AScorebar):
	def __init__(self, frames):
		AScorebar.__init__(self, frames)

	def add_to_frame(self, background):
		AScorebar.animate(self)
		super().add_to_frame(background, 0, -self.h, alpha=self.alpha, topleft=True)
