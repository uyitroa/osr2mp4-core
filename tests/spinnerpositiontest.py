import os
import unittest

from PIL import Image

from utils import getdrawer, abspath
from helper import assert_image_similar, contain_image


class TestSpinnerPosition(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.update = False
		cls.tests.append(getdrawer("4", "syunn", (10, 20)))


	def testframes(self):
		for i in range(len(self.tests)):
			drawer = self.tests[i][1]
			osu_d = {"time": 0, "end time": 10, "id": 0}
			drawer.component.spinner.add_spinner(osu_d, 1)
			drawer.component.spinner.spinners["0o"].alpha = 1
			drawer.component.spinner.update_spinner("0o", 100, 1)
			drawer.component.spinner.add_to_frame(drawer.pbuffer, "0o", "blank")
			expectf = self.tests[i][0] + "spinner.png"

			if self.update:
				drawer.pbuffer.convert("RGB").save(expectf)
			else:
				expect = Image.open(expectf)
				img = drawer.pbuffer.convert("RGB").crop((500 * drawer.settings.scale, 200 * drawer.settings.scale, 1000 * drawer.settings.scale, 400 * drawer.settings.scale))
				img.save("test.png")
				contain = False

				for x in range(90, 110):
					newimg = img.resize((int(img.size[0] * x/100), int(img.size[1] * x/100)))
					contain = contain or contain_image(expect, newimg, 0.98)
				self.assertTrue(contain)




if __name__ == '__main__':
	unittest.main()
