from osr2mp4.ImageProcess.PrepareFrames.YImage import YImage

scorebarbg = "scorebar-bg"


def prepare_scorebarbg(scale, backgroundframe, settings):
	"""
	:param settings:
	:param backgroundframe: [Pillow.Image] second index is the gameplay background
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImage(scorebarbg, settings, scale).img
	return [img]

