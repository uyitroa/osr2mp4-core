def prepare_scorecounter(scorenumber):
	"""
	:param scorenumber: ScoreNumber
	:return: [PIL.Image]
	"""
	img = []
	for image in scorenumber.score_images:
		image.change_size(0.8, 0.8)
		img.append(image.img)
	return img
