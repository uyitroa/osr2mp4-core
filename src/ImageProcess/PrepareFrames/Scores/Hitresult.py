from ImageProcess.Animation import size
from ImageProcess.PrepareFrames.YImage import YImages
from global_var import Settings

hitprefix = "hit"
default_size = 128
hitresult_size = 1.7


def prepare_hitresults(scale, beatmap):

	cs = (54.4 - 4.48 * beatmap.diff["CircleSize"]) * scale
	scale = cs * 2 * hitresult_size / default_size

	scores_frames = {}
	for x in [0, 50, 100, 300]:
		yimg = YImages(hitprefix + str(x), scale, delimiter="-", rotate=x == 0)
		f = []
		f1 = yimg.frames
		if yimg.unanimate:
			img = yimg.frames[0]
			f = []
			if x != 0:
				f = size.grow(img, 0.8, 1.1, 0.05)

			f1 = size.shrink(img, 1.1, 0.9, 0.02)
		if x == 0:
			for a in range(len(f1)):
				f1[a] = f1[a].rotate(10 + a)
		scores_frames[x] = f+f1

	return scores_frames
