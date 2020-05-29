from ....EEnum.EImageFrom import ImageFrom
from ...PrepareFrames.YImage import YImage, YImages

scorebar = "scorebar-colour"
scorebarmarker = "scorebar-marker"

def prepare_scorebar(scale):
	"""
	:param scale: float
	:return: [PIL.Image]
	"""
	yimg = YImages(scorebar, scale, delimiter="-")
	img = yimg.frames

	defaultpath = yimg.imgfrom == ImageFrom.DEFAULT_X or yimg.imgfrom == ImageFrom.DEFAULT_X2
	yimgmarker = YImage(scorebarmarker, scale, defaultpath=defaultpath, fallback="reeee")
	marker = yimgmarker.img
	hasmarker = yimgmarker.imgfrom != ImageFrom.BLANK
	return img, marker, hasmarker
