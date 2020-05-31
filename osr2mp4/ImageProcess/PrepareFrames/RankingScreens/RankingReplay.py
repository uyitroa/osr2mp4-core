from ...PrepareFrames.YImage import YImage

rankingreplay = "pause-replay"


def prepare_rankingreplay(scale, settings):
	img = YImage(rankingreplay, settings, scale).img

	return [img]
