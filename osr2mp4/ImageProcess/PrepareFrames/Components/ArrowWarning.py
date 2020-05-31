from PIL import Image

from ...PrepareFrames.YImage import YImage


arrowwarning = "arrow-warning"


def prepare_arrowwarning(scale, settings):
	"""
	:param settings:
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImage(arrowwarning, settings, scale).img
	img2 = img.transpose(Image.FLIP_LEFT_RIGHT)

	return [img, img2]
