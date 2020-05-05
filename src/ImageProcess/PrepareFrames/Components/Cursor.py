from PIL import Image

from ImageProcess import imageproc
from ImageProcess.Animation.alpha import fadein
from ImageProcess.PrepareFrames.YImage import YImage


cursor = "cursor"
cursortrail = "cursortrail"


def prepare_cursor(scale):
	"""
	:param path: string of path, without filename
	:param scale: float
	:return: [PIL.Image]
	"""
	yimg = YImage(cursor, scale * 0.75)
	frame = [yimg.img]
	return frame


def prepare_cursortrail(scale):
	"""
	:param path: string
	:param scale: float
	:return: [PIL.Image]
	"""
	yimg = YImage(cursortrail, scale)
	trail_frames = fadein(yimg.img, 0.125, 1, 0.125)
	trail_frames.append(Image.new("RGBA", (1, 1)))

	return trail_frames

