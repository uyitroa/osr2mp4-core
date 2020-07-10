import cv2


class PPCounter:
	def __init__(self, settings):
		self.settings = settings
		self.x = int(self.settings.width * 0.93)
		self.y = int(100 * self.settings.scale)
		self.pp = 0

		font = cv2.FONT_HERSHEY_SIMPLEX
		bottomLeftCornerOfText = (self.x, self.y)
		fontScale = 0.5 * self.settings.scale
		fontColor = (255, 255, 255)
		lineType = 1
		self.args = (bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

	def update_pp(self, pp):
		self.set_pp(pp)

	def set_pp(self, pp):
		self.pp = round(pp, 2)

	def add_to_frame(self, background):
		"""

		:param background: numpy.array
		:return:
		"""

		if not self.settings.settings["Enable PP counter"]:
			return

		cv2.putText(background, str(self.pp) + "pp", *self.args)
