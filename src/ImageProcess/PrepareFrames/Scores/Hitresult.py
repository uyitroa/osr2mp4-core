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
		scores_frames[x] = []
		end = 125
		start = 75
		if x != 0:
			end = 125
			start = 100
			for y in range(start, end, -5):
				a = change_size(img, y / 100, y / 100)
				scores_frames[x].append(a)

		for y in range(end, start, -2):
			a = change_size(img, y / 100, y / 100)
			if x == 0:
				a = a.rotate(-10 - (end - y) / 10)
			scores_frames[x].append(a)
	return scores_frames
