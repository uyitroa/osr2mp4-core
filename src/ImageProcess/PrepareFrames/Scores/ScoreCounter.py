def prepare_scorecounter(scorenumber):
	"""
	:param scorenumber: ScoreNumber
	:return: [PIL.Image]
	"""
	img = []
	for image in scorenumber.score_images:
		image.change_size(0.75, 0.75)
		img.append(image.img)
	return img
