import json


def read(filename):
	fileopen = open(filename, "r", encoding="utf-8")
	text = fileopen.read()
	text = text.replace("\\", "/")
	data = json.loads(text)

	fileopen.close()

	return data
