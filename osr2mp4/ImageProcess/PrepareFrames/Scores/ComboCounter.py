from ...Animation import alpha, size


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
		score_frames.append(f)

		f = size.shrink(score_images[digit].img, 1.8, 1.09, 0.07 * 60/settings.fps)
		f = alpha.fadeout(f, 1.8/3, 1.09/3, 0.07/3 * 60/settings.fps)
		score_fadeout.append(f)
	return score_frames, score_fadeout
