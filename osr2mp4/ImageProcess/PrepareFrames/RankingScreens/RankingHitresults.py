from ....EEnum.EImageFrom import ImageFrom
from ...PrepareFrames.YImage import YImage, YImages

hitprefix = "hit"


def prepare_rankinghitresults(scale):
	scores_frames = {}
	scale *= 0.5
	bonus = {100: "k", 300: "g"}
	for x in [0, 50, 100, 300]:
		yimg = YImage(hitprefix + str(x), scale)
		scores_frames[x] = yimg.img

		if x > 50:
			yimg = YImage(hitprefix + str(x) + bonus[x], scale, fallback="reeee")
			img = yimg.img
			if yimg.imgfrom == ImageFrom.BLANK:
				yimg = YImages(hitprefix + str(x) + bonus[x], scale, delimiter="-")
				img = yimg.frames[0]
			scores_frames[x + 5] = img

	return scores_frames
