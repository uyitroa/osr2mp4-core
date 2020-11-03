import os
import time
from osr2mp4.osr2mp4 import Osr2mp4


def main():
	osr2mp4 = Osr2mp4(filedata="data.json",
	                  filesettings="settings.json",
	                  logtofile=True)

	osr2mp4.startall()
	osr2mp4.joinall()


if __name__ == "__main__":
	asdf = time.time()
	main()
	print("\nTotal time:", time.time() - asdf)
