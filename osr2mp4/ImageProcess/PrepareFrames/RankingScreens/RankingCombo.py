from ...PrepareFrames.YImage import YImages

rankingcombo = "ranking-maxcombo"


def prepare_rankingcombo(scale, settings):
	img = YImages(rankingcombo, settings, scale, "-").frames
	return img
