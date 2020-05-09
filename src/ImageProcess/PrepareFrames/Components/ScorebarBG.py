from ImageProcess.PrepareFrames.YImage import YImage


scorebarbg = "scorebar-bg"


def prepare_scorebarbg(scale):
	"""
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImage(scorebarbg, scale).img

	return [img]

