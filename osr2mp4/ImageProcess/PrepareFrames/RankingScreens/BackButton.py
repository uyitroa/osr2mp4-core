from ...PrepareFrames.YImage import YImages

menuback = "menu-back"


def prepare_menuback(scale, settings):
	img = YImages(menuback, settings, scale, delimiter="-").frames
	return img
