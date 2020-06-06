import os
import unittest

from PIL import Image

from utils import getdrawer, getexpect
from helper import assert_image_similar, getepsilon


class TestCompareFrames(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.update = False
		cls.saveimages = False

		expectimage, videotime, timestamp, epsilon = getexpect("", "syunn")
		cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # followpoints

		expectimage, videotime, timestamp, epsilon = getexpect("1", "syunn")
		cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # followpoints

		# expectimage, videotime, timestamp, epsilon = getexpect("2", "syunn")
		# cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # slider
		# #
		# # expectimage, videotime, timestamp, epsilon = getexpect("3", "syunn")
		# # cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # normal
		# #
		# expectimage, videotime, timestamp, epsilon = getexpect("7", "syunn")
		# cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # slider follwball

		# expectimage, videotime, timestamp, epsilon = getexpect("8", "syunn")
		# cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # miss animation
		#
		# expectimage, videotime, timestamp, epsilon = getexpect("9", "syunn")
		# cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # miss animation
		#
		# expectimage, videotime, timestamp, epsilon = getexpect("10", "syunn")
		# cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # miss animation
		#
		# expectimage, videotime, timestamp, epsilon = getexpect("11", "syunn")
		# cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # miss animation
		#
		# expectimage, videotime, timestamp, epsilon = getexpect("12", "syunn")
		# cls.tests.append((*getdrawer("4", "syunn", videotime), epsilon, expectimage, timestamp))  # miss animation


	def testframes(self):
		blank = Image.new("RGBA", (0, 1))
		for i in range(len(self.tests)):
			drawer = self.tests[i][1]

			found = False
			resultinfo = drawer.updater.resultinfo[drawer.updater.info_index]
			while True:
				if not found:
					drawer.img = blank
				else:
					drawer.img = drawer.pbuffer

				status = drawer.render_draw()
				resultinfo = drawer.updater.resultinfo[drawer.updater.info_index]

				if found and (resultinfo.timestamp != self.tests[i][-1] or type(resultinfo.more).__name__ != "Circle"):
					break
				if resultinfo.timestamp == self.tests[i][-1] and type(resultinfo.more).__name__ == "Circle":
					found = True


			drawer.img = drawer.pbuffer
			# drawer.render_draw()

			img = drawer.img.convert("RGB")
			if self.saveimages:
				img.save("test{}.png".format(i))
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
