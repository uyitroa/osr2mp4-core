from osr2mp4.ImageProcess import imageproc
import numpy as np

def img_fade(img, start, end, step):
	outputs = []
	for x in np.arange(start, end, step):
		im = imageproc.newalpha(img, x)
		outputs.append(im)
	return outputs


def list_fade(img, start, end, step):
	outputs = []
	x = start
	for i in img:
		im = imageproc.newalpha(i, x)
		outputs.append(im)
		x += step
	return outputs


def fadeout(img, start, end, step):
	"""
	:param img: PIL.Image or list of PIL.Image
	:param start: size coef
	:param end: size coef
	:param step: size coef
	:return: list of PIL.Image
	"""
	if type(img).__name__ == 'list':
		return list_fade(img, start, end, -step)
	else:
		return img_fade(img, start, end, -step)


def fadein(img, start, end, step):

	if type(img).__name__ == 'list':
		return list_fade(img, start, end, step)
	else:
		return img_fade(img, start, end, step)

