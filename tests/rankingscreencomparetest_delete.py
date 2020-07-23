import os
import unittest

from PIL import Image

from utils import getdrawer, getexpect
from helper import assert_image_similar, getepsilon


class TestCompareRanking(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.update = False

		expectimage, videotime, timestamp, epsilon = getexpect("5", "syunn")
		cls.tests.append((*getdrawer("5", "syunn", videotime), epsilon, expectimage, timestamp))  # shige copy skin

		expectimage, videotime, timestamp, epsilon = getexpect("6", "syunn")
		cls.tests.append((*getdrawer("6", "syunn", videotime), epsilon, expectimage, timestamp))  # default skin



	def testframes(self):
		for i in range(len(self.tests)):
			drawer = self.tests[i][1]

			for x in range(int(4 * drawer.settings.fps)):
				drawer.draw_rankingpanel()

			drawer.img = drawer.pbuffer

			img = drawer.img.convert("RGB")
			img.save("test.png")
			expect = Image.open(self.tests[i][-2] + ".png").convert("RGB")
			ep = getepsilon(img, expect)
			if self.update:
				fileopen = open(self.tests[i][-2] + "epsilon.txt", "w")
				fileopen.write(str(ep))
				fileopen.close()
			else:
				print(ep, self.tests[i][-3])
				self.assertLessEqual(ep, self.tests[i][-3])



if __name__ == '__main__':
	unittest.main()
