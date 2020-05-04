from ImageProcess.PrepareFrames.YImage import YImage, YImages
from ImageProcess.imageproc import change_size

hitprefix = "hit"


def prepare_hitresults(scale):
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
