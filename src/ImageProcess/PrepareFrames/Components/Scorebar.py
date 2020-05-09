from ImageProcess.PrepareFrames.YImage import YImage, YImages

scorebar = "scorebar-colour"


def prepare_scorebar(scale):
	"""
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImages(scorebar, scale, delimiter="-").frames

	return img
