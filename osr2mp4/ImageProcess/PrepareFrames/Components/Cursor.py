import os

from PIL import Image

from ..YImage import YImage
from ...Animation.alpha import fadein
from ...Animation.size import grow

cursor = "cursor"
cursormiddle = "cursormiddle"
cursortrail = "cursortrail"


def prepare_cursor(scale, settings):
	"""
	:param settings:
	:param path: string of path, without filename
	:param scale: float
	:return: [PIL.Image]
	"""
	default = not os.path.isfile(settings.path + cursor + settings.format)
	yimg = YImage(cursor, settings, scale)
	frame = [yimg.img]
	return frame, default


def prepare_cursormiddle(scale, settings, default=False):
	if default:
		path = settings.default_path
	else:
		path = settings.path

	exists = os.path.isfile(path + cursormiddle + settings.format)
	yimg = YImage(cursormiddle, settings, scale, defaultpath=default, fallback="reeeee")
	frame = [yimg.img]

	return frame, exists


def prepare_cursortrail(scale, continuous, settings):
	"""
	:param path: string
	:param scale: float
	:return: [PIL.Image]
	"""

	if continuous:
		end = 1.5
	else:
		end = 1
	yimg = YImage(cursortrail, settings, scale)
	trail_frames = fadein(yimg.img, 0.1, end, 0.1 * 60/settings.fps)
	trail_frames = grow(trail_frames, 0.9, 1, 0.1/9 * 60/settings.fps)
	trail_frames.append(Image.new("RGBA", (1, 1)))

	return trail_frames

