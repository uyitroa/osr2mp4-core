def prepare_rankingscorecounter(scorenumber):
	"""
	:param scorenumber: ScoreNumber
	:return: [PIL.Image]
	"""
	img = {}
	hitresultimg = {}
	c = 0
	for image in scorenumber.score_images:
		image.change_size(1.2999, 1.2999)
		img[c] = image.img

		image.change_size(1, 1)
		hitresultimg[c] = image.img
		c += 1
	scorenumber.score_dot.change_size(1, 1)
	hitresultimg["."] = scorenumber.score_dot.img

	scorenumber.combo_x.change_size(1, 1)
	hitresultimg["x"] = scorenumber.score_x.img

	scorenumber.score_percent.change_size(1, 1)
	hitresultimg["%"] = scorenumber.score_percent.img
	return img, hitresultimg
