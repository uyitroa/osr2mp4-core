import glob
import unittest
import bruh
from osr2mp4.Parser.skinparser import Skin
from utils import getskins


class TestScore(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.update = False
		cls.tests = getskins()

	def testskin(self):
		for i in range(len(self.tests)):
			s = Skin("", "", inipath=self.tests[i])
			result = str(s.colours) + "\n" + str(s.fonts)
			if self.update:
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
