from ImageProcess.PrepareFrames.YImage import YImage

hitprefix = "hit"


def prepare_rankinghitresults(scale):
	scores_frames = {}
	scale *= 0.5
	bonus = {100: "k", 300: "g"}
	for x in [0, 50, 100, 300]:
		yimg = YImage(hitprefix + str(x), scale)
		scores_frames[x] = yimg.img

		if x > 50:
			yimg = YImage(hitprefix + str(x) + bonus[x], scale)
			scores_frames[x + 5] = yimg.img

	return scores_frames
