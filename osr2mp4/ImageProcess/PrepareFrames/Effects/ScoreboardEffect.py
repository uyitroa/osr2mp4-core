from PIL import Image, ImageDraw

from ... import imageproc


def prepare_scoreboardeffect(scale):
	image = Image.new('RGBA', (int(1366 * scale), int(768 * scale)))
	draw = ImageDraw.Draw(image)
	alpha = 0
	width = 1366 * scale
	height = 0
	x = 0
	y = 768 * scale * 0.5
	speed = 5 * scale
	speedalpha = 0
	for i in range(50):
		draw.ellipse((x, y, x + width, y + height), fill=(255, 255, 255, int(alpha)),
		             outline=(255, 255, 255, int(alpha)))
		alpha = min(200, alpha + speedalpha)
		x += 1.5 * scale
		y -= speed
		width -= 3 * scale
		height += speed * 2
		speed = max(0.00001, speed - 0.75 * scale)
		speedalpha = min(15, speedalpha + 0.05 * scale)

	eclipseeffect = image.crop((int(image.size[0] * 3/5), y, image.size[0], y + height))
	eclipseeffect = imageproc.change_size(eclipseeffect, 2.25, 2.5)

	image = Image.new('RGBA', (int(1366 * scale), int(768 * scale)))
	draw = ImageDraw.Draw(image)
	alpha = 0
	width = 1366 * scale
	height = 768 * scale
	x = 0
	y = 0
	speedalpha = 0
	for i in range(50):
		draw.ellipse((x, y, x + width, y + height), fill=(255, 255, 255, int(alpha)),
		             outline=(255, 255, 255, int(alpha)))
		alpha = min(170, alpha + speedalpha)
		x += 1.5 * scale
		y += 0.3 * scale
		width -= 4
		height -= 0.6 * scale
		speedalpha = min(10, speedalpha + 0.15 * scale)
	circleeffect = image.crop((int(image.size[0] * 9 / 10), int(image.size[1] * 2 / 10), image.size[0], int(image.size[1] * 8 / 10)))
	circleeffect = imageproc.change_size(circleeffect, 0.5, 0.5)
	return [eclipseeffect, circleeffect]

