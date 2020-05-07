import hashlib
import os


def get_osu(path, maphash):
	filelist = os.listdir(path)
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
