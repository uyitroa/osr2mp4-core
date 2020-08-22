from ... import imageproc

from ..YImage import YImage

urarrow = "editor-rate-arrow"


def prepare_urarrow(settings):
	frame = YImage(urarrow, settings, settings.scale * settings.settings["Score meter size"] * 0.75, defaultpath=True).img
	imageproc.changealpha(frame, 0.85)
	return [frame]

