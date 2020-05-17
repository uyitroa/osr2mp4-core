import unittest

from CheckSystem.checkmain import checkmain
from global_var import Settings
from test.utils import getinfos


class TestScore(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		Settings.timeframe = 1000
		Settings.fps = 60
		cls.tests.append(getinfos("../test/resources/", "dearbrave"))
		cls.tests.append(getinfos("../test/resources/", "2dearbrave"))
		cls.tests.append(getinfos("../test/resources/", "3dearbrave"))
		cls.tests.append(getinfos("../test/resources/", "yomi"))
		cls.tests.append(getinfos("../test/resources/", "tool"))
		cls.tests.append(getinfos("../test/resources/", "2tool"))
		cls.tests.append(getinfos("../test/resources/", "2yomi"))
		cls.tests.append(getinfos("../test/resources/", "4yomi"))
		cls.tests.append(getinfos("../test/resources/", "reimei", True))
		cls.tests.append(getinfos("../test/resources/", "1reimei"))
		# cls.tests.append(getinfos("../test/resources/", "2reimei"))
		# cls.tests.append(getinfos("../test/resources/", "blends"))

	def testscore(self):
		for i in range(len(self.tests)):
			case = self.tests[i]
			for x in range(len(case[1])):
				print("FDJFIDJF")
				resultinfo = checkmain(case[0], case[2][x], case[1][x], 0, True)
				self.assertEqual(case[2][x].number_300s, resultinfo[-1].accuracy[300], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))
				self.assertEqual(case[2][x].number_100s, resultinfo[-1].accuracy[100], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))
				self.assertEqual(case[2][x].number_50s, resultinfo[-1].accuracy[50], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))
				self.assertEqual(case[2][x].number_50s, resultinfo[-1].accuracy[50], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))
				self.assertEqual(case[2][x].score, int(resultinfo[-1].score), msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))


if __name__ == '__main__':
	unittest.main()
