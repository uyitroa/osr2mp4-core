import json


def read(filename):
	text = open(filename, "r").read()
	text = text.replace("\\", "/")
	data = json.loads(text)

	return data
