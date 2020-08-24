from osr2mp4.ImageProcess.PrepareFrames.YImage import YImages

rankingcombo = "ranking-maxcombo"


def prepare_rankingcombo(scale, settings):
	img = YImages(rankingcombo, settings, scale, "-").frames
	return img
