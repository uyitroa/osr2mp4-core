from ImageProcess.PrepareFrames.YImage import YImage


hitprefix = "hit"


def prepare_hitresults(scale):
	scores_frames = {}
	for x in [0, 50, 100]:
		img = YImage(hitprefix + str(x), scale, rotate=x == 0)
		scores_frames[x] = []
		end = 125
		start = 75
		if x != 0:
			end = 125
			start = 100
			for y in range(start, end, -5):
				img.change_size(y / 100, y / 100)
				scores_frames[x].append(img.img)

		for y in range(end, start, -2):
			img.change_size(y / 100, y / 100)
			a = img.img
			if x == 0:
				a = a.rotate(-10 - (end - y) / 10)
			scores_frames[x].append(a)
	return scores_frames
