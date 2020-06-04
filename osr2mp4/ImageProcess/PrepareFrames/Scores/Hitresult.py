from ...Animation import size
from ...PrepareFrames.YImage import YImages

hitprefix = "hit"
default_size = 128
hitresult_size = 1.7


def prepare_hitresults(scale, beatmap, settings):

	cs = (54.4 - 4.48 * beatmap.diff["CircleSize"]) * scale
	scale = cs * 2 * hitresult_size / default_size

	scores_frames = {}
	for x in [0, 50, 100, 300]:
		yimg = YImages(hitprefix + str(x), settings, scale, delimiter="-", rotate=x == 0)
		f = []
		f1 = yimg.frames
		if yimg.unanimate:
			img = yimg.frames[0]
			f = []
			if x != 0:
				f = size.grow(img, 0.7, 1.1, 0.05)

		if x == 0:
			if yimg.unanimate:
				f1 = f1[0]
			f1 = size.shrink(f1, 1.45, 0.9, 0.05)
			f = []
			# for a in range(len(f1)):
			# 	f1[a] = f1[a].rotate(-10 - a * 0.5)
		scores_frames[x] = f+f1

	return scores_frames
