from PIL import Image

from ...PrepareFrames.YImage import YImage


arrowwarning = "arrow-warning"


def prepare_arrowwarning(scale):
	"""
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImage(arrowwarning, scale).img
	img2 = img.transpose(Image.FLIP_LEFT_RIGHT)

	return [img, img2]
