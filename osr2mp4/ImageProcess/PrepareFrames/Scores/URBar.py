from PIL import Image


def prepare_bar(scale, scorewindow):
	"""
	:param scale: float
	:param scorewindow: [float]
	:return: PIL.Image, [PIL.Image], float
	"""
	scale = scale * scorewindow[2]/100
	w, h = int(160 * scale), int(20 * scale)
	bar_images = []

	colors = [(255, 200, 77, 175), (89, 255, 9, 175), (44, 186, 255, 175)]

	barheight = int(h / 4)
	maxtime = scorewindow[2]
	widths = [int(w), int(scorewindow[1] / maxtime * w), int(scorewindow[0] / maxtime * w)]
	xstart = [0, (w - widths[1]) // 2, (w - widths[2]) // 2]


	colorbar = [(255, 220, 100, 100), (110, 255, 30, 100), (70, 210, 255, 100)]
	for i in range(3):
		cc = [*colorbar[:3], 5]
		bar = Image.new("RGBA", (int(3 * scale), h), cc[i])
		bar.paste(colorbar[i], (int(1.5 * scale), 0, int(2.5 * scale), h))
		bar_images.append(bar)

	urbar = Image.new("RGBA", (w, h))
	for i in range(len(xstart)):
		urbar.paste(colors[i], (xstart[i], h//2 - barheight//2, xstart[i] + widths[i], h//2 + barheight//2))

	return urbar, bar_images, maxtime

