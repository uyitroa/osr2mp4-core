import numpy as np
from PIL import Image

from ... import imageproc


def prepare_background(backgroundname, settings):
	"""
	:param backgroundname: string
	:return: PIL.Image
	"""
	try:
		img = Image.open(backgroundname).convert("RGBA")
	except Exception as e:
		img = Image.open(settings.path + "res/bg.png").convert("RGBA")

	width = settings.width
	height = settings.height
	ratiow = width / height
	ratioh = height / width

	w = min(img.size[0], int(img.size[1] * ratiow))
	h = min(img.size[1], int(img.size[0] * ratioh))
	x, y = (img.size[0] - w)//2, (img.size[1] - h)//2
	img = img.crop((x, y, x + w, y + h))

	scale = width/w
	img = imageproc.change_size(img, scale, scale)
	imgs = [Image.new("RGBA", (1, 1))]

	dim = max(0, min(100, (100 - settings.settings["Background dim"]))) * 2.55
	color = np.array([dim, dim, dim])
	interval = int(1000/60)
	c_interval = max(0, (settings.settings["Background dim"] - 50) * 2.55/interval)
	color[:] = color[:] - c_interval
	for x in range(interval):
		color[:] = color[:] + c_interval
		a = imageproc.add_color(img, color)
		imgs.append(a)
	return imgs
