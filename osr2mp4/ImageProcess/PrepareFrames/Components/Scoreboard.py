from ... import imageproc
from ...PrepareFrames.YImage import YImage


scoreboard = "menu-button-background"


def prepare_scoreboard(scale, settings):
	"""
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImage(scoreboard, settings, scale).img
	img = img.crop((int(img.size[0] * 2/3), 0, img.size[0], img.size[1]))
	img = img.resize((int(140 * scale), int(64 * scale)))
	imageproc.changealpha(img, 0.3)

	playerimg = imageproc.add_color(img, [80, 80, 80])
	img = imageproc.add_color(img, [60, 70, 120])
	return [img, playerimg]

