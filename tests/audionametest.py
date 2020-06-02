import unittest
import bruh
from utils import getaudiofilename


class TestAudio(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.test = []
		cls.test.append(getaudiofilename("audiodearbrave"))
		cls.test.append(getaudiofilename("audioyomi"))
		cls.test.append(getaudiofilename("audioyomi2"))
		cls.test.append(getaudiofilename("audioyomi3"))
		cls.test.append(getaudiofilename("audioyomi4"))

	def testaudioname(self):
		counter = 0
		for case in self.test:
			print(case)
			print(counter)
			self.assertCountEqual(case[0], case[1])
			counter += 1

if __name__ == '__main__':
	unittest.main()
