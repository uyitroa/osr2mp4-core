import unittest

from osr2mp4.CheckSystem.HitObjectChecker import difficulty_multiplier
from osr2mp4.global_var import Settings
from utils import getinfos, getbeatmap


class TestScore(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		Settings.timeframe = 1000
		Settings.fps = 60
		cls.tests.append([difficulty_multiplier(getbeatmap("reimei", "../test/resources/").diff), 4])
		cls.tests.append([difficulty_multiplier(getbeatmap("dareka", "../test/resources/").diff), 4])
		cls.tests.append([difficulty_multiplier(getbeatmap("blends", "../test/resources/").diff), 4])
		cls.tests.append([difficulty_multiplier(getbeatmap("blends2", "../test/resources/").diff), 5])
		cls.tests.append([difficulty_multiplier(getbeatmap("nobore", "../test/resources/").diff), 5])



	def testscore(self):
		for i in range(len(self.tests)):
			self.assertEqual(self.tests[i][0], self.tests[i][1], msg="case {}".format(str(i)))


if __name__ == '__main__':
	unittest.main()
