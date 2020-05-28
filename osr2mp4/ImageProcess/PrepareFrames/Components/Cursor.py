import os

from PIL import Image

from ...Animation.alpha import fadein
from ...Animation.size import grow
from ...PrepareFrames.YImage import YImage, SkinPaths
from ....global_var import Settings

cursor = "cursor"
cursormiddle = "cursormiddle"
cursortrail = "cursortrail"


def prepare_cursor(scale):
	"""
	:param path: string of path, without filename
	:param scale: float
	:return: [PIL.Image]
	"""
	default = not os.path.isfile(SkinPaths.path + cursor + SkinPaths.format)
	yimg = YImage(cursor, scale)
	frame = [yimg.img]
	return frame, default


def prepare_cursormiddle(scale, default=False):
	if default:
		path = SkinPaths.default_path
	else:
		path = SkinPaths.path

	exists = os.path.isfile(path + cursormiddle + SkinPaths.format)
	yimg = YImage(cursormiddle, scale, defaultpath=default, fallback="reeeee")
	frame = [yimg.img]

	return frame, exists


def prepare_cursortrail(scale, continuous):
	"""
	:param path: string
	:param scale: float
	:return: [PIL.Image]
	"""

	if continuous:
		end = 1.5
	else:
		end = 1
	yimg = YImage(cursortrail, scale)
	trail_frames = fadein(yimg.img, 0.1, end, 0.1 * 60/Settings.fps)
	trail_frames = grow(trail_frames, 0.9, 1, 0.1/9 * 60/Settings.fps)
	trail_frames.append(Image.new("RGBA", (1, 1)))

	return trail_frames

