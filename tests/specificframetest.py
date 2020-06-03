import os
import unittest

from PIL import Image

from utils import getdrawer, abspath
from helper import assert_image_similar


class TestSpecificFrame(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.update = False
		cls.tests.append(getdrawer("", "syunn", (10, 20)))  # default skin
		cls.tests.append(getdrawer("2", "syunn", (60, 70)))
		cls.tests.append(getdrawer("3", "syunn", (107, 115)))  # has scoreboard effect animation


	def testframes(self):
		blank = Image.new("RGBA", (0, 1))
		for i in range(len(self.tests)):
			drawer = self.tests[i][1]

			counter = 0

			while counter <= 100:
				if not counter % 10 == 0:
					drawer.img = blank

				status = drawer.render_draw()
				if status:
					if counter % 10 == 0:
						expectf = self.tests[i][0] + "frameat{}.png".format(counter)
						if self.update:
							drawer.pbuffer.save(expectf)
						else:
							expect = Image.open(expectf).convert("RGBA")
							assert_image_similar(drawer.pbuffer, expect, 1)
					counter += 1


if __name__ == '__main__':
	unittest.main()
