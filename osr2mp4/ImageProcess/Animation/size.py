import numpy as np
from PIL import Image

from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.Animation import easings

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



""" EPIC VERSION """
def img_resize_(img: Image, start: float, end: float, delta: float, duration: float, easing: easings):
	res = []
	
	for time in np.arange(0, duration, delta):
		size_val = easing(time, start, end, duration)
		res.append(imageproc.change_size(img, size_val, size_val))
		
	return res
	
def list_resize_(imgs: [Image], start: float, end: float, duration: float, easing: easings):
	res = []
	delta = duration/len(imgs)
	cur_time = 0
	
	for img in imgs:
		size_val = easing(cur_time, start, end, duration)
		res.append(imageproc.change_size(img, size_val, size_val))
		cur_time += delta
		
	return res
	
def resize(imgs: Image, start: float, end: float, duration: float, settings: 'settings', easing: easings = easings.easeLinear):
	delta = settings.timeframe/settings.fps
	end = end-start
	
	if isinstance(imgs, list):
		return list_resize_(imgs, start, end, duration, easing)
	else:
		return img_resize_(imgs, start, end, delta, duration, easing)
	
	
