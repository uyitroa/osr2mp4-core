

def prepare_accuracy(scorenumbers):
	"""
	:param scorenumbers: Scorenumber
	:return: int, [PIL.Image]
	"""
	score_images = {}
	y = int(scorenumbers.score_images[0].img.size[1])
	for index, img in enumerate(scorenumbers.score_images):
		img.change_size(0.5, 0.5)
		score_images[index] = img.img
	scorenumbers.score_percent.change_size(0.6, 0.6)
	score_images["%"] = scorenumbers.score_percent.img

	scorenumbers.score_dot.change_size(0.5, 0.5)
	score_images["."] = scorenumbers.score_dot.img

	return score_images, y
