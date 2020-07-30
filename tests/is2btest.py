import os
import unittest

from osr2mp4.Parser.osuparser import read_file

from utils import abspath


class TestSliderfollow(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.non2b = []

		cls.non2b.append("onegai")
		cls.non2b.append("logic")
		cls.non2b.append("etude")
		cls.non2b.append("technical")
		cls.non2b.append("galaxy")
		cls.non2b.append("sanae")

		cls.is2b = []
		cls.is2b.append("mope")
		cls.is2b.append("tewi")
		cls.is2b.append("degrees")

	def test_non2b(self):
		for i in range(len(self.non2b)):
			case = read_file(os.path.join(abspath, self.non2b[i] + ".osu"), lazy=False)
			print(f"Checking {case.path}")
			self.assertFalse(case.is2b, msg=f"{case.path} is not 2b")

	def test_2b(self):
		for i in range(len(self.is2b)):
			case = read_file(os.path.join(abspath, self.is2b[i] + ".osu"), lazy=False)
			print(f"Checking {case.path}")
			self.assertTrue(case.is2b, msg=f"{case.path} is 2b")




if __name__ == '__main__':
	unittest.main()
