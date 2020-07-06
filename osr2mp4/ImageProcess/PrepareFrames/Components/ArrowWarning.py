from PIL import Image

from osr2mp4.EEnum.EImageFrom import ImageFrom
from ...PrepareFrames.YImage import YImage


arrowwarning = "arrow-warning"
playwarningarrow = "play-warningarrow"


def prepare_arrowwarning(scale, settings):
	"""
	:param settings:
	:param scale: float
	:return: [PIL.Image]
	"""
	yimg = YImage(arrowwarning, settings, scale)
	if yimg.imgfrom == ImageFrom.BLANK:
		yimg = YImage(playwarningarrow, settings, scale)
	img = yimg.img
	img2 = img.transpose(Image.FLIP_LEFT_RIGHT)

	return [img, img2]
