def prepare_rankingscorecounter(scorenumber):
	"""
	:param scorenumber: ScoreNumber
	:return: [PIL.Image]
	"""
	img = []
	hitresultimg = []
	for image in scorenumber.score_images:
		image.change_size(1.2999, 1.2999)
		img.append(image.img)

		image.change_size(1, 1)
		hitresultimg.append(image.img)
	scorenumber.score_dot.change_size(1, 1)
	hitresultimg.append(scorenumber.score_dot.img)

	scorenumber.combo_x.change_size(1, 1)
	hitresultimg.append(scorenumber.score_x.img)

	scorenumber.score_percent.change_size(1, 1)
	hitresultimg.append(scorenumber.score_percent.img)
	return img, hitresultimg
