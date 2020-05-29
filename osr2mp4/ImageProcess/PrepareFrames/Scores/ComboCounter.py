from ... import imageproc
from ...Animation import alpha, size
from ....global_var import Settings


def prepare_combo(scorenumbers):
	"""
	:param scorenumbers: ScoreNumbers
	:return: [PIL.Image], [PIL.Image]
	"""
	score_frames = []
	score_fadeout = []
	score_images = scorenumbers.combo_images
	score_images.append(scorenumbers.combo_x)
	for digit in range(len(score_images)):
		f = size.grow(score_images[digit].img, 1, 1.2, 0.03 * 60/Settings.fps)
		score_frames.append(f)

		f = size.shrink(score_images[digit].img, 1.8, 1.09, 0.07 * 60/Settings.fps)
		f = alpha.fadeout(f, 1.8/3, 1.09/3, 0.07/3 * 60/Settings.fps)
		score_fadeout.append(f)
	print(len(score_fadeout[0]))
	return score_frames, score_fadeout
