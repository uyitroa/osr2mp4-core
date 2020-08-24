from osr2mp4.ImageProcess import imageproc


def prepare_spinbonus(scorenumber):
	score_frames = []
	for image in scorenumber.score_images:
		score_frames.append([])
		size = 2.5
		for x in range(15, 5, -1):
			img = imageproc.change_size(image.img, size, size, rows=image.orig_rows, cols=image.orig_cols)
			score_frames[-1].append(imageproc.newalpha(img, x / 15))
			size -= 0.1
	return score_frames
