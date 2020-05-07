import numpy as np
from PIL import Image

from ImageProcess import imageproc
from global_var import Settings


def prepare_background(backgroundname):
	"""
	:param backgroundname: string
	:return: PIL.Image
	"""
	print(backgroundname)
	img = Image.open(backgroundname).convert("RGBA")

	width = Settings.width
	height = Settings.height
	ratiow = width / height
	ratioh = height / width

	w = min(img.size[0], int(img.size[1] * ratiow))
	h = min(img.size[1], int(img.size[0] * ratioh))
	img = img.crop((0, 0, w, h))

	scale = width/w
	img = imageproc.change_size(img, scale, scale)
	imgs = [Image.new("RGBA", (1, 1))]

	color = np.array([0, 0, 0])
	interval = int(650/Settings.fps)
	c_interval = 100/interval
	for x in range(interval):
		color[:] = color[:] + c_interval
		a = imageproc.add_color(img, color)
		imgs.append(a)
	return imgs
