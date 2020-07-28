import unittest
from osr2mp4.CheckSystem.checkmain import checkmain
from osr2mp4.global_var import Settings
from utils import getinfos


class TestSliderfollow(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.settings = Settings()
		cls.settings.timeframe = 1000
		cls.settings.fps = 60
		cls.tests.append(getinfos("milkcrown", hr=True))
		cls.tests.append(getinfos("future", hr=True, dt=True))
		cls.tests.append(getinfos("bubble", hr=True))

	def test_sliderfollow(self):
		for i in range(len(self.tests)):
			case = self.tests[i]
			print(f"Checking {case[0].path}")

			for x in range(len(case[1])):
				name = x
				if x == 0:
					name = ""
				print(f"Replay {case[2]}{name}.osr")

				resultinfo = checkmain(case[0], case[1][x], self.settings, True)
				self.assertEqual(case[1][x].misses, resultinfo[-1].accuracy[0], msg="replay {} case {} {}".format(str(x), str(i), str(case[1][x].timestamp)))


if __name__ == '__main__':
	unittest.main()
