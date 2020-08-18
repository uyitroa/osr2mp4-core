import numpy
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

	colors = [(218, 174, 70, 200), (87, 227, 19, 200), (50, 188, 231, 200)]

	barheight = int(h / 4)
	maxtime = scorewindow[2]
	widths = [int(w), int(scorewindow[1] / maxtime * w), int(scorewindow[0] / maxtime * w)]
	xstart = [0, (w - widths[1]) // 2, (w - widths[2]) // 2]

	colorbar = [(210, 160,  60, 255), (70, 215, 10, 255), (40, 170, 220, 255)]
	mask = []
	for i in range(3):
		bar = numpy.full((int(2 * scale), 4), colorbar[i])
		bar_images.append(bar)

		m = min(colorbar[i]) * 2
		r = m/colorbar[i][0]
		g = m/colorbar[i][1]
		b = m/colorbar[i][2]
		mask.append([r, g, b, 4])

	urbar = Image.new("RGBA", (w, h))
	masknp = numpy.zeros((w, 4))
	for i in range(len(xstart)):
		urbar.paste(colors[i], (xstart[i], h//2 - barheight//2, xstart[i] + widths[i], h//2 + barheight//2))
		masknp[xstart[i]:xstart[i]+widths[i], :] = mask[i]

	return urbar, bar_images, maxtime, masknp

