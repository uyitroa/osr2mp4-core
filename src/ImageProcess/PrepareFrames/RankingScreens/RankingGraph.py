from ...PrepareFrames.YImage import YImage, YImages

rankinggraph = "ranking-graph"
rankingperfect = "ranking-perfect"


def prepare_rankinggraph(scale):
	img = YImage(rankinggraph, scale).img
	perfectimg = YImages(rankingperfect, scale, delimiter="-").frames[0]


	return [img, perfectimg]
