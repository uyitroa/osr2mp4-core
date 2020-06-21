from PIL import Image
import numpy as np

from ....EEnum.EImageFrom import ImageFrom
from ...Animation.size import shrink
from ...PrepareFrames.YImage import YImage
from ... import imageproc

scoreentry = "scoreentry-"
inputoverlay = "inputoverlay-key"
bg = "inputoverlay-background"


def prepare_scoreentry(scale, color, settings):
	"""
	:param settings:
	:param path: string of path, without filename
	:param scale: float
	:param color: tuple(R, G, B)
	:return: [PIL.Image]
	"""
	numbers_animation = []
	for x in range(10):
		number = YImage(scoreentry + str(x), settings, scale)
		if number.imgfrom == ImageFrom.BLANK:
			img = Image.open(settings.path + "res/" + scoreentry + str(x) + "@2x.png")
			img = imageproc.change_size(img, scale * 0.5, scale * 0.5)
		else:
			img = number.img
		tmp = imageproc.add_color(img, color)
		numbers_animation.append(shrink(tmp, 0.9, 0.3, 0.05 * 60/settings.fps))
	return numbers_animation


def prepare_inputoverlay(scale, color, index_c, settings):
	"""
	:param settings:
	:param scale: float
	:param color: tuple(R, G, B)
	:param index_c: index of the color that changes (fadeout fadein)
	:return: [PIL.Image]
	"""
	yimg = YImage(inputoverlay, settings, scale)
	color = np.array(color)
	color[index_c] += 200
	color[color > 255] = 255

	start, end, step = 1, 0.77, 0.05 * 60/settings.fps
	c_step = int(200*step/(start - end - step))

	button_frames = shrink(yimg.img, start, end, step)
	for i, img in enumerate(button_frames):
		imgc = imageproc.add_color(img, color)
		button_frames[i] = imgc
		color[index_c] = max(0, color[index_c] - c_step)
	button_frames.insert(0, yimg.img)
	return button_frames


def prepare_inputoverlaybg(scale, settings):
	"""
	:param settings:
	:param path: string of path, without filename
	:param scale: float
	:return: [PIL.Image]
	"""
	yimg = YImage(bg, settings, scale, scaley=scale * 1.05)
	img = yimg.img.transpose(Image.ROTATE_270)
	frame = [img]
	return frame
