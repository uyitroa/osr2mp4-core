from ImageProcess.PrepareFrames.YImage import YImage


scorebar = "scorebar-bg"


def prepare_scorebar(scale):
	"""
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImage(scorebar, scale).img

	return [img]
