from ImageProcess.Animation import size
from ImageProcess.PrepareFrames.YImage import YImages
from ImageProcess.imageproc import change_size

hitprefix = "hit"
default_size = 128
hitresult_size = 2


def prepare_hitresults(scale, beatmap):

	cs = (54.4 - 4.48 * beatmap.diff["CircleSize"]) * scale
	scale = cs * 2 * hitresult_size / default_size

	scores_frames = {}
	for x in [0, 50, 100]:
		img = YImages(hitprefix + str(x), scale, delimiter="-", rotate=x == 0).frames[0]
		f = []
		if x != 0:
			f = size.grow(img, 1, 1.25, 0.05)

		f1 = size.shrink(img, 1.25, 1, 0.02)
		if x == 0:
			for a in range(len(f1)):
				f1[a] = f1[a].rotate(10 + a)
		scores_frames[x] = f+f1
	return scores_frames
