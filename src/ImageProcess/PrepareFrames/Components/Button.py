from PIL import Image

from ImageProcess.PrepareFrames.YImage import YImage
from ImageProcess import imageproc

scoreentry = "scoreentry-"
inputoverlay = "inputoverlay-key"
bg = "inputoverlay-background"


def prepare_scoreentry(scale, color):
	"""
	:param path: string of path, without filename
	:param scale: float
	:param color: tuple(R, G, B)
	:return: [PIL.Image]
	"""
	numbers_animation = []
	for x in range(10):
		number = YImage(scoreentry + str(x), scale)
		numbers_animation.append([])
		tmp = imageproc.add_color(number.img, color)
		for size in range(95, 77, -3):
			size /= 100
			numbers_animation[-1].append(imageproc.change_size(tmp, size, size))
	return numbers_animation


def prepare_inputoverlay(scale, color):
	"""
	:param scale: float
	:param color: tuple(R, G, B)
	:return: [PIL.Image]
	"""
	yimg = YImage(inputoverlay, scale)

	button_frames = [yimg.img]
	for size in range(97, 82, -3):
		size /= 100
		yimg.change_size(size, size)
		img = imageproc.add_color(yimg.img, color)

		button_frames.append(img)

	return button_frames


def prepare_inputoverlaybg(scale):
	"""
	:param path: string of path, without filename
	:param scale: float
	:return: [PIL.Image]
	"""
	yimg = YImage(bg, scale)
	img = yimg.img.transpose(Image.ROTATE_270)
	frame = [img]
	return frame
