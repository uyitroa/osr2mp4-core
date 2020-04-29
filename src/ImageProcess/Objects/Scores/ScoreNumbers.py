from ImageProcess.PrepareFrames.YImage import YImage


class ScoreNumbers:
	def __init__(self, info, path, scale):
		self.score_images = []
		scoreprefix = info["ScorePrefix"] + "-"
		score_x = scoreprefix + "x"
		score_percent = scoreprefix + "percent"
		score_dot = scoreprefix + "dot"
		for x in range(10):
			self.score_images.append(YImage(path + scoreprefix + str(x), scale))
		self.score_x = YImage(path + score_x, scale)

		self.score_percent = YImage(path + score_percent, scale)

		self.score_dot = YImage(path + score_dot, scale)
