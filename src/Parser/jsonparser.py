import json
from json.decoder import JSONDecodeError


def permissive_json_loads(text):
	while True:
		try:
			data = json.loads(text)
		except JSONDecodeError as exc:
			if exc.msg == 'Invalid \\escape':
				text = text[:exc.pos] + '\\' + text[exc.pos:]
			else:
				raise
		else:
			return data


def read(filename):
	text = open(filename, "r").read()
	data = permissive_json_loads(text)
	return data
