def prepare_scorecounter(scorenumber):
	"""
	:param scorenumber: ScoreNumber
	:return: [PIL.Image]
	"""
	img = []
	for image in scorenumber.score_images:
		image.change_size(0.87, 0.87)
		img.append(image.img)
	return img
