from ImageProcess import imageproc


def prepare_combo(scorenumbers):
	"""
	:param scorenumbers: ScoreNumbers
	:return: [PIL.Image], [PIL.Image]
	"""
	score_frames = []
	score_fadeout = []
	score_images = scorenumbers.score_images
	score_images.append(scorenumbers.score_x)
	for digit in range(len(score_images)):
		score_frames.append([])
		score_fadeout.append([])
		for x in range(100, 131, 3):
			score_images[digit].change_size(x / 100, x / 100)
			normal = score_images[digit].img
			score_frames[-1].append(normal)

		for x in range(180, 109, -7):
			score_images[digit].change_size(x / 100, x / 100)
			fadeout = imageproc.newalpha(score_images[digit].img, (x / 300))
			score_fadeout[-1].append(fadeout)
	return score_frames, score_fadeout
