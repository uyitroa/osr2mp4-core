from ...PrepareFrames.YImage import YImage

rankingtitle = "ranking-title"


def prepare_rankingtitle(scale, settings):
	img = YImage(rankingtitle, settings, scale).img

	return [img]
