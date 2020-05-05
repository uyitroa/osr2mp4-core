from ImageProcess import imageproc


def img_fade(img, start, end, step):
	outputs = []
	for x in range(start, end, step):
		im = imageproc.newalpha(img, x/100)
		outputs.append(im)
	return outputs


def list_fade(img, start, end, step):
	outputs = []
	index = 0
	for x in range(start, end, step):
		im = imageproc.newalpha(img[index], x / 100)
		outputs.append(im)
		index += 1
	return outputs


def fadeout(img, start, end, step):
	"""
	:param img: PIL.Image or list of PIL.Image
	:param start: size coef
	:param end: size coef
	:param step: size coef
	:return: list of PIL.Image
	"""
	start = int(start * 100)
	end = int(end * 100)
	step = int(step * 100)

	if type(img).__name__ == 'list':
		return list_fade(img, end, start, -step)
	else:
		return img_fade(img, end, start, -step)


def fadein(img, start, end, step):
	start = int(start * 100)
	end = int(end * 100)
	step = int(step * 100)

	if type(img).__name__ == 'list':
		return list_fade(img, start, end, step)
	else:
		return img_fade(img, start, end, step)

