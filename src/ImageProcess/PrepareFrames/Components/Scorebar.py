from ImageProcess.PrepareFrames.YImage import YImage
from global_var import Settings


scorebar = "scorebar-bg"


def prepare_scorebar(scale):
	"""
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImage(scorebar, scale).img

	# width = Settings.width
	# height = Settings.height
	# ratiow = width / height
	# ratioh = height / width
	#
	# w = min(img.size[0], int(img.size[1] * ratiow))
	# h = min(img.size[1], int(img.size[0] * ratioh))
	# img = img.crop((0, 0, w, h))

	return [img]
