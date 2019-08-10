from Objects.abstracts import Images

scoreprefix = "score-"
score_x = "score-x.png"
score_percent = "score-percent.png"
score_dot = "score-dot.png"


class ScoreNumbers:
	def __init__(self, path, scale, simulate):
		self.score_images = []
		for x in range(10):
			self.score_images.append(Images(path + scoreprefix+str(x)+".png", scale, simulate=simulate))
			self.score_images[-1].to_3channel()
		self.score_x = Images(path + score_x, scale, simulate=simulate)
		self.score_x.to_3channel()

		self.score_percent = Images(path + score_percent, scale, simulate=simulate)
		self.score_percent.to_3channel()

		self.score_dot = Images(path + score_dot, scale, simulate=simulate)
		self.score_dot.to_3channel()
