import os

from PIL import Image

from osr2mp4.EEnum.EImageFrom import ImageFrom
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.PrepareFrames.YImage import YImage


scoreentry = "scoreentry-"


def scorelist_to_dict(frames):
	frames_dict = {}
	for i in range(len(frames)):
		x = i
		if i == 10:
			x = "x"
		if i == 11:
			x = "."
		frames_dict[x] = frames[i]
	return frames_dict


def prepare_scoreboardscore(scale, settings):
	"""
	:param settings:
	:param path: string of path, without filename
	:param scale: float
	:param color: tuple(R, G, B)
	:return: [PIL.Image]
	"""

	scale = scale * 0.8

	numbers_animation = []
	for x in range(12):
		if x == 10:
			x = "x"
		if x == 11:
			x = "dot"
		number = YImage(scoreentry + str(x), settings, scale)

		if number.imgfrom == ImageFrom.BLANK:
			img = Image.open(os.path.join(settings.path, "res", scoreentry + str(x) + "@2x.png"))
			img = imageproc.change_size(img, scale * 0.5, scale * 0.5)
		else:
			img = number.img

		numbers_animation.append(img)
	combo_number = imageproc.change_sizes(numbers_animation, 0.9, 0.9)
	combo_number = imageproc.add_color_s(combo_number, [200, 255, 255])
	combo_number = scorelist_to_dict(combo_number)

	bigger_numbers_animation = imageproc.change_sizes(numbers_animation, 2, 2)
	bigger_numbers_animation = scorelist_to_dict(bigger_numbers_animation)

	numbers_animation = scorelist_to_dict(numbers_animation)
	return numbers_animation, bigger_numbers_animation, combo_number
