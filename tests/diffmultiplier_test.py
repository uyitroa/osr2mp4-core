import os
import unittest

from osr2mp4.Parser.osuparser import read_file

from osr2mp4.CheckSystem.HitObjectChecker import difficulty_multiplier
from utils import abspath


class TestScore(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.tests.append(["reimei", 4])
		cls.tests.append(["dareka", 4])
		cls.tests.append(["blends", 4])
		cls.tests.append(["blends2", 5])
		cls.tests.append(["nobore", 5])

	def testscore(self):
		for i in range(len(self.tests)):
			mappath = os.path.join(abspath, self.tests[i][0] + ".osu")
			print(f"Checking {mappath}")

			result = difficulty_multiplier(read_file(mappath).diff)
			expect = self.tests[i][1]
			self.assertEqual(result, expect, msg="case {}".format(str(i)))


if __name__ == '__main__':
	unittest.main()
