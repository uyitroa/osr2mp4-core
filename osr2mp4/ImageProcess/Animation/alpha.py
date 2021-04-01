import numpy as np
from PIL import Image

from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.Animation import easings



def img_fade(img: Image, start: float, end: float, step: float):
	outputs = []
	for x in np.arange(start, end, step):
		im = imageproc.newalpha(img, x)
		outputs.append(im)
	return outputs


def list_fade(img: [Image], start: float, end: float, step: float):
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
		
		
""" Gaming Version """
def img_fade_(img: Image, start: float, end: float, delta: float, duration: float, easing: easings):
	res = []
	
	for time in np.arange(0, duration, delta): # for now
		fade_val = easing(time, start, end, duration)
		res += [imageproc.newalpha(img, fade_val)]
		
	return res
	
def list_fade_(imgs: [Image], start: float, end: float, duration: float, easing: easings):
	res = []
	delta = duration/len(imgs)
	cur_time = 0
	
	for img in imgs:
		fade_val = easing(cur_time, start, end, duration)
		res += [imageproc.newalpha(img, fade_val)]
		cur_time += delta
		
	return res
	
def fade(imgs: Image, start: float, end: float, duration: float, settings: 'settings', easing: easings = easings.easeLinear):
	delta = settings.timeframe/settings.fps
	end = end-start
	
	if isinstance(imgs, list):
		return list_fade_(imgs, start, end, duration, easing)
	else:
		return img_fade_(imgs, start, end, delta, duration, easing)
		
		

