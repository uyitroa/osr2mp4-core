from ImageProcess.PrepareFrames.YImage import YImage


default_circle_size = 128


def prepare_hitcirclenumber(path, fonts, diff, scale):
	"""
	:param path: string path without filename
	:param fonts: skin fonts
	:param diff:
	:param scale:
	:return: [PIL.Image]
	"""
	circle_radius = (54.4 - 4.48 * diff["CircleSize"]) * scale * 0.9
	hitcircle_number = []
	scale = circle_radius * 2 / default_circle_size
	for x in range(10):
		img = YImage("{}{}-{}".format(path, fonts["HitCirclePrefix"], str(x)), scale)
		hitcircle_number.append(img.img)
	return hitcircle_number
