from ...PrepareFrames.YImage import YImages

rankingaccuracy = "ranking-accuracy"


def prepare_rankingaccuracy(scale, settings):
	img = YImages(rankingaccuracy, settings, scale, delimiter="-").frames
	return img
