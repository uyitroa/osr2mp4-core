import glob
import os
import unittest
from osr2mp4.Parser.skinparser import Skin
from utils import abspath


class TestScore(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.update = False
		skinpath = os.path.join(abspath, "skininis", "*.ini")
		cls.tests = glob.glob(skinpath)

	def testskin(self):
		for i in range(len(self.tests)):
			s = Skin("", "", inipath=self.tests[i])
			result = str(s.colours) + "\n" + str(s.fonts)

			if self.update:  # ignore this if
				fwrite = open(self.tests[i] + ".result", "w")
				fwrite.write(result)
				fwrite.close()
			else:
				fread = open(self.tests[i] + ".result", "r")
				expectresult = fread.read()
				fread.close()

				self.assertEqual(expectresult, result)


if __name__ == '__main__':
	unittest.main()
