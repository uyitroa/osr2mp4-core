from osr2mp4.ImageProcess import imageproc


def prepare_accuracy(scorenumbers):
	"""
	:param scorenumbers: Scorenumber
	:return: int, [PIL.Image]
	"""
	score_images = {}
	y = int(scorenumbers.score_images[0].img.size[1])
	for index, img in enumerate(scorenumbers.score_images):
		imgacc = imageproc.change_size(img.img, 0.5, 0.5)
		score_images[index] = imgacc
	imgacc = imageproc.change_size(scorenumbers.score_percent.img, 0.6, 0.6)
	score_images["%"] = imgacc

	imgacc = imageproc.change_size(scorenumbers.score_dot.img, 0.5, 0.5)
	score_images["."] = imgacc

	return score_images, y
