from ...PrepareFrames.YImage import YImage, YImages

rankinggraph = "ranking-graph"
rankingperfect = "ranking-perfect"


def prepare_rankinggraph(scale, settings):
	img = YImage(rankinggraph, settings, scale).img
	perfectimg = YImages(rankingperfect, settings, scale, delimiter="-").frames[0]


	return [img, perfectimg]
