import hashlib


def osuhash(filename):
	md5 = hashlib.md5()
	with open(filename, 'rb') as b:
		while True:
			data = b.read(1)
			if not data:
				break
			md5.update(data)
	m = md5.hexdigest()
	return m
