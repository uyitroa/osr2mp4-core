from Objects.abstracts import Images


class ScoreNumbers:
	def __init__(self, info, path, scale):
		self.score_images = []
		scoreprefix = info["ScorePrefix"] + "-"
		score_x = scoreprefix + "x"
		score_percent = scoreprefix + "percent"
		score_dot = scoreprefix + "dot"
		for x in range(10):
			self.score_images.append(Images(path + scoreprefix+str(x), scale))
		self.score_x = Images(path + score_x, scale)

		self.score_percent = Images(path + score_percent, scale)

		self.score_dot = Images(path + score_dot, scale)
