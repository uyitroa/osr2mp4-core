from osr2mp4.ImageProcess import imageproc
import numpy as np


def img_resize(img, start, end, step):
	outputs = []
	if not step:
		step = 1
	for x in np.arange(start, end, step):
		im = imageproc.change_size(img, x, x)
		outputs.append(im)
	return outputs


def list_resize(img, start, end, step):
	outputs = []
	x = start
	for i in img:
		im = imageproc.change_size(i, x, x)
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

	if type(img).__name__ == 'list':
		return list_resize(img, start, end, -step)
	else:
		return img_resize(img, start, end, -step)


def grow(img, start, end, step):

	if type(img).__name__ == 'list':
		return list_resize(img, start, end, step)
	else:
		return img_resize(img, start, end, step)

