import os
from .maphash import osuhash
from ..Exceptions import BeatmapNotFound


def get_osu(path, maphash):
	try:
		filelist = os.listdir(path)
	except FileNotFoundError as e:
		raise BeatmapNotFound() from None
	for f in filelist[:]:
		if f.endswith(".osu"):
			m = osuhash(os.path.join(path, f))
			if maphash == m:
				return os.path.join(path, f)

	raise BeatmapNotFound()
