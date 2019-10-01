from Objects.abstracts import Images

scoreprefix = "score-"
score_x = "score-x"
score_percent = "score-percent"
score_dot = "score-dot"


class ScoreNumbers:
	def __init__(self, path, scale):
		self.score_images = []
		for x in range(10):
			self.score_images.append(Images(path + scoreprefix+str(x), scale))

		self.score_x = Images(path + score_x, scale)

		self.score_percent = Images(path + score_percent, scale)

		self.score_dot = Images(path + score_dot, scale)
