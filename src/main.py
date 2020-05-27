import os
from Parser.jsonparser import read
from VideoProcess.DiskUtils import convert_tomp4
import time
from osr2mp4 import Osr2mp4


def main():

	data = read("config.json")

	gameplaydata = read("settings.json")

	osr2mp4 = Osr2mp4(data, gameplaydata)
	osr2mp4.startall()
	osr2mp4.joinall()

	if os.name != 'nt':
		convert_tomp4()


if __name__ == "__main__":
	asdf = time.time()
	main()
	print("\nTotal time:", time.time() - asdf)
