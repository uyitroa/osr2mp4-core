from ImageProcess.PrepareFrames.YImage import YImage

rankingreplay = "ranking-replay"


def prepare_rankingreplay(scale):
	img = YImage(rankingreplay, scale).img

	return [img]
