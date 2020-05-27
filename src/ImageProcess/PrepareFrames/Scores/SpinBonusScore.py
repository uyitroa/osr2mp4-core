from ... import imageproc


def prepare_spinbonus(scorenumber):
	score_frames = []
	for image in scorenumber.score_images:
		score_frames.append([])
		size = 2.5
		for x in range(15, 5, -1):
			image.change_size(size, size)
			score_frames[-1].append(imageproc.newalpha(image.img, x / 15))
			size -= 0.1
	return score_frames
