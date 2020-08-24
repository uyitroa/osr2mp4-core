from osr2mp4.ImageProcess.Animation.easing import easingout
from osr2mp4.ImageProcess.Objects.Scores.ACounter import ACounter


class PPCounter(ACounter):
	def __init__(self, settings):
		super().__init__(settings, settings.ppsettings)
		self.score = str(0.00)
		self.realscore = 0
		self.timeframe = self.settings.timeframe / self.settings.fps
		self.first = True

	def update(self, pp):
		self.realscore = pp
		if self.first:
			self.set(pp)
			self.first = False

	def set(self, pp):
		self.score = "{:.2f}".format(pp)

	def add_to_frame(self, background):

		score = float(self.score)

		super().add_to_frame(background)

		current = self.timeframe
		change = self.realscore - score
		duration = 500

		score = max(0, easingout(current, score, change, duration))

		self.score = "{:.2f}".format(score)
