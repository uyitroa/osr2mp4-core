from ...PrepareFrames.YImage import YImages

rankingaccuracy = "ranking-accuracy"


def prepare_rankingaccuracy(scale):
	img = YImages(rankingaccuracy, scale, delimiter="-").frames
	return img
