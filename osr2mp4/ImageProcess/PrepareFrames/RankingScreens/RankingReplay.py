from ... import imageproc
from ...PrepareFrames.YImage import YImage

rankingreplay = "pause-replay"


def prepare_rankingreplay(scale, settings):
	img = YImage(rankingreplay, settings, scale).img
	img = imageproc.newalpha(img, 0.4)

	return [img]
