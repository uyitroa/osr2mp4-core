from ...PrepareFrames.YImage import YImages

rankingcombo = "ranking-maxcombo"


def prepare_rankingcombo(scale):
	img = YImages(rankingcombo, scale, "-").frames
	return img
