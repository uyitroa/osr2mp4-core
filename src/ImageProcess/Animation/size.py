from ImageProcess import imageproc


def img_resize(img, start, end, step):
	outputs = []
	for x in range(start, end, step):
		im = imageproc.change_size(img, x/100, x/100)
		outputs.append(im)
	return outputs


def list_reisze(img, start, end, step):
	outputs = []
	index = 0
	for x in range(start, end, step):
		im = imageproc.change_size(img[index], x/100, x/100)
		outputs.append(im)
		index += 1
	return outputs


def shrink(img, start, end, step):
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
		return list_reisze(img, end, start, -step)
	else:
		return img_resize(img, end, start, -step)


def grow(img, start, end, step):
	start = int(start * 100)
	end = int(end * 100)
	step = int(step * 100)

	if type(img).__name__ == 'list':
		return list_reisze(img, start, end, step)
	else:
		return list_reisze(img, start, end, step)

