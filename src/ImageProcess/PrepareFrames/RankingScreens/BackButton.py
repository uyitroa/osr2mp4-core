from ...PrepareFrames.YImage import YImages

menuback = "menu-back"


def prepare_menuback(scale):
	img = YImages(menuback, scale, delimiter="-").frames
	return img
