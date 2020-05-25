from PIL import Image


def prepare_bar(scale, scorewindow):
	"""
	:param scale: float
	:param scorewindow: [float]
	:return: PIL.Image, [PIL.Image], float
	"""
	scale = scale * scorewindow[2]/100
	w, h = int(200 * scale), int(25 * scale)
	bar_images = []

	colors = [(255, 200, 77, 175), (89, 255, 9, 175), (44, 186, 255, 175)]

	barheight = int(h / 5)
	maxtime = scorewindow[2]
	widths = [int(w), int(scorewindow[1] / maxtime * w), int(scorewindow[0] / maxtime * w)]
	xstart = [0, (w - widths[1]) // 2, (w - widths[2]) // 2]

	for i in range(3):
		bar_images.append(Image.new("RGBA", (4, h), colors[i]))

	urbar = Image.new("RGBA", (w, h))
	for i in range(len(xstart)):
		urbar.paste(colors[i], (xstart[i], barheight * 2, xstart[i] + widths[i], barheight * 3))

	return urbar, bar_images, maxtime

