from .ACounter import ACounter


class PPCounter(ACounter):
	def __init__(self, settings):
		super().__init__(settings, settings.ppsettings)
		self.score = str(0.00)

	def update(self, pp):
		self.set(pp)

	def set(self, pp):
		self.score = "{:.2f}".format(pp)
