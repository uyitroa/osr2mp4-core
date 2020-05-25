import unittest
from ImageProcess.Objects.Components.Scoreboard import getmods


class TestModDiff(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		aa = open('../test/resources/mods.txt', 'r')
		a = aa.readlines()
		cls.mods = [eval(x) for x in a]
		aa.close()

		aa = open('../test/resources/modsexpect.txt', 'r')
		a = aa.readlines()
		cls.modsexpect = [eval(x) for x in a]
		aa.close()

	def test_mods(self):
		for x in range(len(self.mods)):
			self.assertListEqual(getmods(self.mods[x]), self.modsexpect[x])



if __name__ == '__main__':
	unittest.main()
