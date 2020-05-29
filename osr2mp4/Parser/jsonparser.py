import json


def read(filename):
	text = open(filename, "r", encoding="utf-8").read()
	text = text.replace("\\", "/")
	data = json.loads(text)

	return data
