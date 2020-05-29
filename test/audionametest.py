import unittest

from utils import getaudiofilename


class TestAudio(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.test = []
		cls.test.append(getaudiofilename("audiodearbrave", "../test/resources/"))
		cls.test.append(getaudiofilename("audioyomi", "../test/resources/"))
		cls.test.append(getaudiofilename("audioyomi2", "../test/resources/"))
		cls.test.append(getaudiofilename("audioyomi3", "../test/resources/"))
		cls.test.append(getaudiofilename("audioyomi4", "../test/resources/"))

	def testaudioname(self):
		counter = 0
		for case in self.test:
			print(case)
			print(counter)
			for i in range(len(case[1])):
				folder = case[1][i]
				for name in folder:
					self.assertTrue(name in case[0][i], msg="{} not in case[0][{}]".format(name, i))

			for i in range(len(case[0])):
				folder = case[0][i]
				for name in folder:
					self.assertTrue(name in case[1][i], msg="{} not in case[1][{}]".format(name, i))
			counter += 1

if __name__ == '__main__':
	unittest.main()
