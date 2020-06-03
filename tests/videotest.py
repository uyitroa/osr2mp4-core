import atexit
import os
import unittest

from PIL import Image
import bruh
from osr2mp4.EEnum.EReplay import Replays
from osr2mp4.osr2mp4 import Osr2mp4
from utils import getdrawer, getexpect, getrightconfigs, get_length, get_res


def cleanup(tests):
	for i in range(len(tests)):
		filename = tests[i].settings.output
		os.remove(filename)


class TestCompareFrames(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.update = False
		cls.saveimages = False

		cls.tests.append(Osr2mp4(*getrightconfigs("10")))
		cls.tests[-1].startall()
		cls.tests[-1].joinall()

		cls.tests.append(Osr2mp4(*getrightconfigs("11")))
		cls.tests[-1].startall()
		cls.tests[-1].joinall()


		if True:  # to be able to disable sometimes for testing
			atexit.register(cleanup, cls.tests)

	def testlength(self):
		for i in range(len(self.tests)):
			osr2mp4 = self.tests[i]

			expectlength = 0
			starttime = osr2mp4.starttimne
			endtime = osr2mp4.endtime
			if osr2mp4.endtime == -1:
				expectlength += 5
				endtime = osr2mp4.replay_event[osr2mp4.end_index][Replays.TIMES] / osr2mp4.settings.timeframe
			expectlength += endtime - starttime

			outputlength = get_length(osr2mp4.settings.output)
			print(outputlength, expectlength)
			self.assertLessEqual(abs(expectlength - outputlength), 2)


	def testresolution(self):
		for i in range(len(self.tests)):
			osr2mp4 = self.tests[i]

			expectwidth = osr2mp4.settings.width
			expectheight = osr2mp4.settings.height

			outputwidth, outputheight = get_res(osr2mp4.settings.output)
			self.assertEqual(expectwidth, outputwidth)
			self.assertEqual(expectheight, outputheight)


if __name__ == '__main__':
	unittest.main()
