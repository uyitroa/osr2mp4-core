import os
import unittest

from PIL import Image

from utils import getdrawer, abspath
from helper import assert_image_similar


class TestRankingScreen(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.update = False
		cls.tests.append(getdrawer("", "syunn", (123123123, -1)))
		cls.tests.append(getdrawer("2", "syunn", (123123123, -1)))


	def testframes(self):
		for i in range(len(self.tests)):
			drawer = self.tests[i][1]

			expectf = self.tests[i][0] + "rankingbruh.png"

			for x in range(int(0.5 * drawer.settings.fps)):
				drawer.draw_rankingpanel()

			if self.update:
				drawer.pbuffer.save(expectf)
			else:
				expect = Image.open(expectf).convert("RGBA")
				assert_image_similar(drawer.pbuffer, expect, 5)


			expectf = self.tests[i][0] + "rankingbruh1.png"

			for x in range(int(0.6 * drawer.settings.fps)):
				drawer.draw_rankingpanel()

			if self.update:
				drawer.pbuffer.save(expectf)
			else:
				expect = Image.open(expectf).convert("RGBA")
				assert_image_similar(drawer.pbuffer, expect, 1)


if __name__ == '__main__':
	unittest.main()
