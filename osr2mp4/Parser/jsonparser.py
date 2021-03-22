import json

def read(filename):
	with open(filename, 'r', encoding='utf-8') as file:
		data = json.loads(file.read())

	return data
