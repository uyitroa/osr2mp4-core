from ...PrepareFrames.YImage import YImage

rankingreplay = "pause-replay"


def prepare_rankingreplay(scale):
	img = YImage(rankingreplay, scale).img

	return [img]
