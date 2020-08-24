from PIL import Image
from PIL.ImageDraw import ImageDraw

from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.PrepareFrames.Components.Text import prepare_text


def rounded_rectangle(self: ImageDraw, xy, corner_radius, fill=None, outline=None):
	upper_left_point = xy[0]
	bottom_right_point = xy[1]
	self.rectangle(
		[
			(upper_left_point[0], upper_left_point[1] + corner_radius),
			(bottom_right_point[0], bottom_right_point[1] - corner_radius)
		],
		fill=fill,
		outline=outline
	)
	self.rectangle(
		[
			(upper_left_point[0] + corner_radius, upper_left_point[1]),
			(bottom_right_point[0] - corner_radius, bottom_right_point[1])
		],
		fill=fill,
		outline=outline
	)
	self.pieslice(
		[upper_left_point, (upper_left_point[0] + corner_radius * 2, upper_left_point[1] + corner_radius * 2)],
		180,
		270,
		fill=fill,
		outline=outline
	)
	self.pieslice(
		[(bottom_right_point[0] - corner_radius * 2, bottom_right_point[1] - corner_radius * 2), bottom_right_point],
		0,
		90,
		fill=fill,
		outline=outline
	)
	self.pieslice([(upper_left_point[0], bottom_right_point[1] - corner_radius * 2),
					(upper_left_point[0] + corner_radius * 2, bottom_right_point[1])],
					90,
					180,
					fill=fill,
					outline=outline
					)
	self.pieslice([(bottom_right_point[0] - corner_radius * 2, upper_left_point[1]),
	               (bottom_right_point[0], upper_left_point[1] + corner_radius * 2)],
					270,
					360,
					fill=fill,
					outline=outline
					)


def prepare_rankingur(settings, ur):
	"""
	:param settings: Settings
	:param ur: [error -, error +, ur]
	:return:
	"""
	error_ = "{:.2f}".format(ur[0])
	error = "{:.2f}".format(ur[1])
	ur = "{:.2f}".format(ur[2])
	text = ["Accuracy:", f"Error {error_}ms - {error}ms avg", f"Unstable Rate: {ur}"]
	scale = settings.scale * 1.3
	width = int(scale * 350)
	height = int(width * 9 / 16 * len(text)/6)

	image = Image.new("RGBA", (width, height))
	d = ImageDraw(image)
	rounded_rectangle(d, ((0, 0), (width, height)), 20, fill=(255, 255, 255, 200))
	rounded_rectangle(d, ((2, 2), (width - 2, height - 2)), 15, fill=(0, 0, 0, 200))

	texti = prepare_text(text, scale * 20, (255, 255, 255), settings)
	y = height * 0.025
	for t in texti:
		imageproc.add(texti[t], image, width * 0.01, y, topleft=True)
		y += texti[t].size[1] + 5 * settings.scale

	image = image.resize((width // 2, height // 2))
	return [image]
