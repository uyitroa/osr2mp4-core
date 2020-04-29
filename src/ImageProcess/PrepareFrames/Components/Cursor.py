from ImageProcess import imageproc
from ImageProcess.PrepareFrames.YImage import YImage


cursor = "cursor"
cursortrail = "cursortrail"


def prepare_cursor(path, scale):
	"""
	:param path: string of path, without filename
	:param scale: float
	:return: [PIL.Image]
	"""
	yimg = YImage(path + cursor, scale * 0.75)
	frame = [yimg.img]
	return frame


def prepare_cursortrail(path, scale):
	"""
	:param path: string
	:param scale: float
	:return: [PIL.Image]
	"""
	yimg = YImage(path + cursortrail, scale * 0.75)
	trail_frames = []
	for x in [0.2, 0.35, 0.55, 0.65, 0.75, 0.9, 1, 0]:
		img = imageproc.newalpha(yimg.img, x)
		trail_frames.append(img)

	return trail_frames

