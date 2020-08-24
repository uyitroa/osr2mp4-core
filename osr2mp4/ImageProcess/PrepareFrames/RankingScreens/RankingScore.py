from osr2mp4.ImageProcess import imageproc


def prepare_rankingscorecounter(scorenumber):
	"""
	:param scorenumber: ScoreNumber
	:return: [PIL.Image]
	"""
	img = {}
	hitresultimg = {}
	c = 0
	for image in scorenumber.score_images:
		imgscore = imageproc.change_size(image.img, 1.2999, 1.2999)
		img[c] = imgscore

		hitresultimg[c] = image.img
		c += 1
	imgscore = imageproc.change_size(scorenumber.score_dot.img, 1, 1)
	hitresultimg["."] = imgscore

	imgscore = imageproc.change_size(scorenumber.combo_x.img, 1, 1)
	hitresultimg["x"] = imgscore

	imgscore = imageproc.change_size(scorenumber.score_percent.img, 1, 1)
	hitresultimg["%"] = imgscore
	return img, hitresultimg
