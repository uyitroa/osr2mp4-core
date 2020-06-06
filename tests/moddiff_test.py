import unittest
import bruh
from osr2mp4.CheckSystem.checkmain import dtod, dtar, htod, htar
from utils import abspath


class TestModDiff(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		aa = open('{}htod.txt'.format(abspath), 'r')
		a = aa.readlines()
		cls.htod = [float(x) for x in a]
		aa.close()

		aa = open('{}dtod.txt'.format(abspath), 'r')
		a = aa.readlines()
		cls.dtod = [float(x) for x in a]
		aa.close()

		aa = open('{}htar.txt'.format(abspath), 'r')
		a = aa.readlines()
		cls.htar = [float(x) for x in a]
		aa.close()

		aa = open('{}dtar.txt'.format(abspath), 'r')
		a = aa.readlines()
		cls.dtar = [float(x) for x in a]
		aa.close()

	def test_dtod(self):
		for x in range(11):
			self.assertEqual(self.dtod[x], float(dtod(x)), "DTOD wrong")

	def test_htod(self):
		for x in range(11):
			self.assertEqual(self.htod[x], float(htod(x)), "HTOD wrong")

	def test_dtar(self):
		for x in range(11):
			self.assertEqual(self.dtar[x], float(dtar(x)), "DTAR wrong")

	def test_htar(self):
		for x in range(11):
			self.assertEqual(self.htar[x], float(htar(x)), "HTAR wrong")


if __name__ == '__main__':
	unittest.main()
