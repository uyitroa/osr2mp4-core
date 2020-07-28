from PIL import Image, ImageDraw


def prepare_flashlight(settings, hasfl):
	if not hasfl:
		blank = Image.new("RGBA", (1, 1))
		return [blank, blank, blank, blank]
	width = int(settings.width * 2)
	height = int(settings.height * 2)

	fl_radius = 150 * settings.scale
	fl_radius_100combo = fl_radius * 3.2
	fl_radius_200combo = fl_radius * 2.6
	fl_radius_bigcombo = fl_radius * 2
	fl_radius_break = fl_radius * 8

	fl_radiuses = [fl_radius_100combo, fl_radius_200combo, fl_radius_bigcombo, fl_radius_break]

	fl_img = []

	for fl_r in fl_radiuses:
		black = Image.new("RGBA", (width, height), (0, 0, 0, 255))
		draw = ImageDraw.Draw(black)

		alpha = 220
		layer = 500
		step = alpha/layer * 10

		x = width//2 - fl_r//2
		y = height//2 - fl_r//2

		step_r = fl_r/layer

		for i in range(layer):
			z = int(i * settings.scale * step_r)
			draw.ellipse((x + z, y + z, x + fl_r - z, y + fl_r - z), fill=(0, 0, 0, int(alpha)))
			alpha -= step
			alpha = max(0, alpha)
		fl_img.append(black)
	return fl_img

