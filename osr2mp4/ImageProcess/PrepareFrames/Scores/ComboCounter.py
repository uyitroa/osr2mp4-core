from osr2mp4.ImageProcess.Animation import alpha, size


def prepare_combo(scorenumbers, settings):
	"""
	:param scorenumbers: ScoreNumbers
	:return: [PIL.Image], [PIL.Image]
	"""
	score_frames = []
	score_fadeout = []
	score_images = scorenumbers.combo_images
	score_images.append(scorenumbers.combo_x)
	for digit in range(len(score_images)):
		f = size.grow(score_images[digit].img, 1, 1.2, 0.03 * 60/settings.fps)
		d = "x" if digit == 10 else digit
		for i in range(len(f)):
			if i >= len(score_frames):
				score_frames.append({})
			score_frames[i][d] = f[i]

		f = size.shrink(score_images[digit].img, 1.7, 1.12, 0.05 * 60/settings.fps)
		f = alpha.fadeout(f, 1.6/3, 1.09/3, 0.07/3 * 60/settings.fps)
		for i in range(len(f)):
			if i >= len(score_fadeout):
				score_fadeout.append({})
			score_fadeout[i][d] = f[i]

	return score_frames, score_fadeout
