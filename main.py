import os
from osr2mp4.Parser.jsonparser import read
from osr2mp4.VideoProcess.DiskUtils import convert_tomp4
import time
from osr2mp4.osr2mp4 import Osr2mp4


def main():

	data = read("osr2mp4/config.json")

	gameplaydata = read("osr2mp4/settings.json")

	osr2mp4 = Osr2mp4(filedata="osr2mp4/config.json", filesettings="osr2mp4/settings.json")
	osr2mp4.startall()
	osr2mp4.joinall()

	if os.name != 'nt':
		convert_tomp4()


if __name__ == "__main__":
	asdf = time.time()
	main()
	print("\nTotal time:", time.time() - asdf)
