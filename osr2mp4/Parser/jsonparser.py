import json

def read(filename: str):
	with open(filename, 'r', encoding='utf-8') as file:
		data = json.load(file)

	return data
