from ...PrepareFrames.YImage import YImage

scorebarbg = "scorebar-bg"


def prepare_scorebarbg(scale, backgroundframe):
	"""
	:param backgroundframe: [Pillow.Image] second index is the gameplay background
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImage(scorebarbg, scale).img
	img2 = backgroundframe[1].copy()

	img2.paste(img, (0, 0), mask=img)
	return [img, img2]

