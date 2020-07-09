import unittest
import bruh
from osr2mp4.CheckSystem.checkmain import checkmain
from osr2mp4.global_var import Settings
from utils import getinfos


class TestScore(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.settings = Settings()
		cls.settings.timeframe = 1000
		cls.settings.fps = 60
		cls.tests.append(getinfos("dearbrave"))
		cls.tests.append(getinfos("2dearbrave"))
		cls.tests.append(getinfos("3dearbrave"))
		cls.tests.append(getinfos("4dearbrave"))
		cls.tests.append(getinfos("5dearbrave"))
		cls.tests.append(getinfos("yomi"))
		cls.tests.append(getinfos("tool"))
		cls.tests.append(getinfos("2tool"))
		cls.tests.append(getinfos("2yomi"))
		cls.tests.append(getinfos("4yomi"))
		cls.tests.append(getinfos("reimei", True))
		cls.tests.append(getinfos("1reimei"))
		# cls.tests.append(getinfos("dareka"))  # TODO: sliderend problem
		# cls.tests.append(getinfos("len"))  # TODO: score error of 9
		# cls.tests.append(getinfos("2reimei"))  # TODO: sliderend problem
		# cls.tests.append(getinfos("blends"))  # TODO: score error of 4

	def testscore(self):
		for i in range(len(self.tests)):
			case = self.tests[i]
			for x in range(len(case[1])):
				resultinfo = checkmain(case[0], case[1][x], self.settings, True)
				self.assertEqual(case[1][x].number_300s, resultinfo[-1].accuracy[300], msg="replay {} case {} {}".format(str(x), str(i), str(case[1][x].timestamp)))
				self.assertEqual(case[1][x].number_100s, resultinfo[-1].accuracy[100], msg="replay {} case {} {}".format(str(x), str(i), str(case[1][x].timestamp)))
				self.assertEqual(case[1][x].number_50s, resultinfo[-1].accuracy[50], msg="replay {} case {} {}".format(str(x), str(i), str(case[1][x].timestamp)))
				self.assertEqual(case[1][x].number_50s, resultinfo[-1].accuracy[50], msg="replay {} case {} {}".format(str(x), str(i), str(case[1][x].timestamp)))
				self.assertEqual(case[1][x].score, int(resultinfo[-1].score), msg="replay {} case {} {}".format(str(x), str(i), str(case[1][x].timestamp)))


if __name__ == '__main__':
	unittest.main()
