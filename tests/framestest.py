import os
import unittest

from PIL import Image

from utils import getframes
from helper import assert_image_similar


class TestFrames(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		update = False
		cls.tests.append(getframes("", "syunn", update))
		cls.tests.append(getframes("2", "syunn", update))
		cls.tests.append(getframes("3", "velier", update))


	def testframes(self):
		for i in range(len(self.tests)):
			frames = self.tests[i][1]
			images = vars(frames)
			for f in images:

				imglist = getattr(frames, f)
				while type(imglist).__name__ == "list" or type(imglist).__name__ == "tuple":
					index = max(0, (len(imglist) - 1) // 2)  # check the middle image
					imglist = imglist[index]

				if type(imglist).__name__ == "Image":
					expectf = self.tests[i][0] + f + ".png"
					if not os.path.isfile(expectf):
						print("Warning: {} not found".format(expectf))
						continue

					print("Comparing {}".format(expectf))
					expectimg = Image.open(expectf).convert("RGBA")
					imglist.save("test.png")
					assert_image_similar(imglist, expectimg, 1)


if __name__ == '__main__':
	unittest.main()
