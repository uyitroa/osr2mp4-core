import unittest
import bruh
from osr2mp4.ImageProcess.Objects.Components.Scoreboard import getmods
import re
from utils import abspath


class AssertionMod(unittest.TestCase):
	def assertSameMod(self, first, second):
		print(first, second)
		self.assertEqual(len(first), len(second), msg="Not same mods amount")

		for i in range(len(first)):
			found = False
			listfirst = set(re.findall("..", first[i]))
			for ii in range(len(second)):
				listsecond = set(re.findall("..", second[ii]))
				if listsecond == listfirst:
					found = True
					break
			if not found:
				raise AssertionError("{} and {} not same mods".format(first[i], second))


class TestModDiff(AssertionMod):

	@classmethod
	def setUpClass(cls):
		aa = open('{}mods.txt'.format(abspath), 'r')
		a = aa.readlines()
		cls.mods = [x.strip() for x in a]
		aa.close()

		aa = open('{}modsexpect.txt'.format(abspath), 'r')
		a = aa.readlines()
		cls.modsexpect = [eval(x) for x in a]
		aa.close()

	def test_mods(self):
		for x in range(len(self.mods)):
			self.assertSameMod(getmods(self.mods[x]), self.modsexpect[x])



if __name__ == '__main__':
	unittest.main()
