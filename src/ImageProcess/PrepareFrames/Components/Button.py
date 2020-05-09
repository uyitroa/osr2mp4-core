from PIL import Image
import numpy as np

from ImageProcess.Animation.size import shrink
from ImageProcess.PrepareFrames.YImage import YImage
from ImageProcess import imageproc
from global_var import Settings

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
		tmp = imageproc.add_color(number.img, color)
		numbers_animation.append(shrink(tmp, 1, 0.3, 0.05 * 60/Settings.fps))
	return numbers_animation


def prepare_inputoverlay(scale, color, index_c):
	"""
	:param scale: float
	:param color: tuple(R, G, B)
	:param index_c: index of the color that changes (fadeout fadein)
	:return: [PIL.Image]
	"""
	yimg = YImage(inputoverlay, scale)
	color = np.array(color)
	color[index_c] += 200
	color[color > 255] = 255

	start, end, step = 1, 0.77, 0.05 * 60/Settings.fps
	c_step = int(200*step/(start - end - step))

	button_frames = shrink(yimg.img, start, end, step)
	for i, img in enumerate(button_frames):
		imgc = imageproc.add_color(img, color)
		button_frames[i] = imgc
		print(color)
		color[index_c] = max(0, color[index_c] - c_step)
	button_frames.insert(0, yimg.img)
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
