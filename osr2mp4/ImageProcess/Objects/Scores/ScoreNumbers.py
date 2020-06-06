from ...PrepareFrames.YImage import YImage


class ScoreNumbers:
	def __init__(self, scale, settings):
		self.score_images = []
		scoreprefix = "-"
		score_x = scoreprefix + "x"
		score_percent = scoreprefix + "percent"
		score_dot = scoreprefix + "dot"
		for x in range(10):
			self.score_images.append(YImage(scoreprefix + str(x), settings, scale, prefix="ScorePrefix"))

		self.score_percent = YImage(score_percent, settings, scale, prefix="ScorePrefix")

		self.score_dot = YImage(score_dot, settings, scale, prefix="ScorePrefix")

		self.score_x = YImage(score_x, settings, scale, prefix="ScorePrefix")

		self.combo_images = []
		for x in range(10):
			self.combo_images.append(YImage(scoreprefix + str(x), settings, scale, prefix="ComboPrefix"))
		self.combo_x = YImage(score_x, settings, scale, prefix="ComboPrefix")
