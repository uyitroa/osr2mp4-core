from osr2mp4.ImageProcess import imageproc


def prepare_scorecounter(scorenumber):
	"""
	:param scorenumber: ScoreNumber
	:return: [PIL.Image]
	"""
	img = []
	for image in scorenumber.score_images:
		imgscore = imageproc.change_size(image.img, 0.87, 0.87)
		img.append(imgscore)
	return img
