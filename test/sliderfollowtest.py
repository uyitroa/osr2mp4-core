import unittest

from osr2mp4.CheckSystem.checkmain import checkmain
from osr2mp4.global_var import Settings
from utils import getinfos


class TestSliderfollow(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.real = []
		cls.tests = []
		cls.custom = []
		cls.custom_expect100 = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0]
		cls.custom_expect50 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		Settings.timeframe = 1000
		Settings.fps = 60
		cls.tests.append(getinfos("../test/resources/", "yomi"))
		cls.tests.append(getinfos("../test/resources/", "tool"))
		cls.tests.append(getinfos("../test/resources/", "2tool"))
		cls.tests.append(getinfos("../test/resources/", "2yomi"))
		# cls.tests.append(getinfos("../test/resources/", "3yomi"))
		cls.tests.append(getinfos("../test/resources/", "4yomi"))

		cls.custom.append(getinfos("../test/resources/", "69tool"))
		cls.custom.append(getinfos("../test/resources/", "69yomi", True))
		cls.custom.append(getinfos("../test/resources/", "70tool"))
		cls.custom.append(getinfos("../test/resources/", "71tool"))
		cls.custom.append(getinfos("../test/resources/", "69kikoku"))
		cls.custom.append(getinfos("../test/resources/", "70kikoku"))
		cls.custom.append(getinfos("../test/resources/", "71kikoku"))
		cls.custom.append(getinfos("../test/resources/", "72yomi", True))
		cls.custom.append(getinfos("../test/resources/", "73yomi", True))
		cls.custom.append(getinfos("../test/resources/", "74yomi", True))
		cls.custom.append(getinfos("../test/resources/", "75yomi", True))
		cls.custom.append(getinfos("../test/resources/", "76yomi", True))
		cls.custom.append(getinfos("../test/resources/", "77yomi", True))
		cls.custom.append(getinfos("../test/resources/", "72tool"))
		cls.custom.append(getinfos("../test/resources/", "73tool"))
		cls.custom.append(getinfos("../test/resources/", "74tool"))
		cls.custom.append(getinfos("../test/resources/", "75tool"))
		cls.custom.append(getinfos("../test/resources/", "76tool"))
		cls.custom.append(getinfos("../test/resources/", "72kikoku"))
		cls.custom.append(getinfos("../test/resources/", "blends"))
		cls.custom.append(getinfos("../test/resources/", "date"))
		# cls.custom.append(getinfos("../test/resources/", "69reimei"))
		# cls.custom.append(getinfos("../test/resources/", "73kikoku")) ## TODO: fix these commented cases
		# cls.custom.append(getinfos("../test/resources/", "74kikoku"))

		cls.real.append(getinfos("../test/resources/", "realtool"))
		cls.real.append(getinfos("../test/resources/", "realyomi", True))
		# cls.real.append(getinfos("../test/resources/", "realkikoku"))
		cls.real.append(getinfos("../test/resources/", "realmagnolia"))


	def test_sliderfollow(self):
		for i in range(len(self.tests)):
			case = self.tests[i]
			for x in range(len(case[1])):
				resultinfo = checkmain(case[0], case[2][x], case[1][x], 0, True)
				self.assertEqual(case[2][x].number_300s, resultinfo[-1].accuracy[300], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))
				self.assertEqual(case[2][x].number_100s, resultinfo[-1].accuracy[100], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))
				self.assertEqual(case[2][x].number_50s, resultinfo[-1].accuracy[50], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))

	def test_sliderfollowcustom(self):
		for i in range(len(self.custom)):
			case = self.custom[i]
			for x in range(len(case[1])):
				resultinfo = checkmain(case[0], case[2][x], case[1][x], 0, True)
				self.assertEqual(self.custom_expect100[i], resultinfo[-1].accuracy[100], msg="custom replay {} case {}".format(str(x), str(i)))
				self.assertEqual(self.custom_expect50[i], resultinfo[-1].accuracy[50], msg="custom replay {} case {}".format(str(x), str(i)))


	def test_real(self):
		for i in range(len(self.real)):
			case = self.real[i]
			for x in range(len(case[1])):
				resultinfo = checkmain(case[0], case[2][x], case[1][x], 0, True)
				self.assertEqual(case[2][x].number_300s, resultinfo[-1].accuracy[300], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))
				self.assertEqual(case[2][x].number_100s, resultinfo[-1].accuracy[100], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))
				self.assertEqual(case[2][x].number_50s, resultinfo[-1].accuracy[50], msg="replay {} case {} {}".format(str(x), str(i), str(case[2][x].timestamp)))



if __name__ == '__main__':
	unittest.main()
