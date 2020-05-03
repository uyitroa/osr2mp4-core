from ImageProcess import imageproc
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
	yimg = YImage(cursortrail, scale * 0.75)
	trail_frames = []
	for x in [0.1, 0.25, 0.4, 0.55, 0.7, 0.85, 1, 0]:
		img = imageproc.newalpha(yimg.img, x)
		trail_frames.append(img)

	return trail_frames

