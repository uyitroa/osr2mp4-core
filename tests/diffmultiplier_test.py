import unittest
import bruh
from osr2mp4.CheckSystem.HitObjectChecker import difficulty_multiplier
from utils import getinfos, getbeatmap


class TestScore(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.tests.append([difficulty_multiplier(getbeatmap("reimei").diff), 4])
		cls.tests.append([difficulty_multiplier(getbeatmap("dareka").diff), 4])
		cls.tests.append([difficulty_multiplier(getbeatmap("blends").diff), 4])
		cls.tests.append([difficulty_multiplier(getbeatmap("blends2").diff), 5])
		cls.tests.append([difficulty_multiplier(getbeatmap("nobore").diff), 5])



	def testscore(self):
		for i in range(len(self.tests)):
			self.assertEqual(self.tests[i][0], self.tests[i][1], msg="case {}".format(str(i)))


if __name__ == '__main__':
	unittest.main()
