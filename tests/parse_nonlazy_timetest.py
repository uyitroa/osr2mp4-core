import os
import unittest

from osr2mp4.Parser.osuparser import read_file

from utils import abspath


class TestScore(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.tests.append("reimei")
		cls.tests.append("dareka")
		cls.tests.append("yomi")
		cls.tests.append("realyomi")
		cls.tests.append("blends")
		cls.tests.append("technical")
		cls.tests.append("mope")
		cls.tests.append("dearbrave")
		cls.tests.append("2dearbrave")
		cls.tests.append("future")
		cls.tests.append("bubble")
		cls.tests.append("degrees")

	def testscore(self):
		for i in range(len(self.tests)):
			mappath = os.path.join(abspath, self.tests[i] + ".osu")
			print(f"Checking {mappath}")

			lazy = read_file(mappath)
			nonlazy = read_file(mappath, lazy=False)
			self.assertEqual(lazy.start_time, nonlazy.start_time, msg="case {}".format(str(i)))
			self.assertAlmostEqual(lazy.end_time, nonlazy.end_time, msg="case {}".format(str(i)), places=3)


if __name__ == '__main__':
	unittest.main()
