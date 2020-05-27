from ...PrepareFrames.YImage import YImage

rankingtitle = "ranking-title"


def prepare_rankingtitle(scale):
	img = YImage(rankingtitle, scale).img

	return [img]
