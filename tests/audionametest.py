import os
import unittest

from osr2mp4.AudioProcess.Utils import getfilenames

from osr2mp4.Parser.osuparser import read_file
from utils import abspath, getlistfromtxt


class TestAudio(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.test = []
		cls.test.append("audiodearbrave")
		cls.test.append("audioyomi")
		cls.test.append("audioyomi2")
		cls.test.append("audioyomi3")
		cls.test.append("audioyomi4")

	def testaudioname(self):
		for mapname in self.test:
			mappath = "{}{}.osu".format(abspath, mapname)
			print(f"Checking {mappath}")
			bmap = read_file(mappath, lazy=False)

			resultlist = getfilenames(bmap, False)
			resultlist = [list(resultlist[0].keys()), list(resultlist[1].keys())]  # reformat to have the same format as expectedlist

			expectedlist = getlistfromtxt(os.path.join(abspath, mapname + "expect.txt"))
			self.assertCountEqual(resultlist, expectedlist)


if __name__ == '__main__':
	unittest.main()
