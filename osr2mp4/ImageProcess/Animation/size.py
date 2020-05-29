from .. import imageproc


def img_resize(img, start, end, step):
	outputs = []
	for x in range(start, end, step):
		im = imageproc.change_size(img, x/1000, x/1000)
		outputs.append(im)
	return outputs


def list_resize(img, start, end, step):
	outputs = []
	x = start
	for i in img:
		im = imageproc.change_size(i, x/1000, x/1000)
		outputs.append(im)
		x += step
	return outputs


def shrink(img, start, end, step):
	"""
	:param img: PIL.Image or list of PIL.Image
	:param start: size coef
	:param end: size coef
	:param step: size coef
	:return: list of PIL.Image
	"""
	start = int(start * 1000)
	end = int(end * 1000)
	step = int(step * 1000)


	if type(img).__name__ == 'list':
		return list_resize(img, start, end, -step)
	else:
		return img_resize(img, start, end, -step)


def grow(img, start, end, step):
	start = int(start * 1000)
	end = int(end * 1000)
	step = int(step * 1000)


	if type(img).__name__ == 'list':
		return list_resize(img, start, end, step)
	else:
		return img_resize(img, start, end, step)

