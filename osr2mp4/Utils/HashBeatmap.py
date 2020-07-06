import hashlib
import logging
import os

from autologging import traced, logged

from ..Exceptions import BeatmapNotFound


@logged(logging.getLogger(__name__))
@traced
def get_osu(path, maphash):
	try:
		filelist = os.listdir(path)
	except FileNotFoundError as e:
		raise BeatmapNotFound() from None
	for f in filelist[:]:
		if f.endswith(".osu"):
			md5 = hashlib.md5()
			with open(path+f, 'rb') as b:
				while True:
					data = b.read(1)
					if not data:
						break
					md5.update(data)
			m = md5.hexdigest()
			if maphash == m:
				return path+f

	raise BeatmapNotFound()
