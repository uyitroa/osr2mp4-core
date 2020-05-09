from ImageProcess.Objects.FrameObject import FrameObject
from ImageProcess.PrepareFrames.Components.AScorebar import AScorebar
from global_var import Settings


class ScorebarBG(AScorebar):
	def __init__(self, frames):
		AScorebar.__init__(self, frames)

	def add_to_frame(self, background):
		AScorebar.animate(self)
		super().add_to_frame(background, 0, -self.h, alpha=self.alpha, topleft=True)
