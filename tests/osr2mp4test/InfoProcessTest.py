import unittest
import bruh2
import bruh
from oppai import *
from osr2mp4.ImageProcess.Objects.Scores.PPCounter import PPCounter
from osr2mp4.InfoProcessor import Updater
from osr2mp4.CheckSystem.checkmain import checkmain
from utils import getinfos, setupenv
from Dummies.ComponentDummy import FrameObjects
from Dummies.SettingDummy import Settings


class InfoProcessTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.tests = []
		cls.settings = Settings()
		cls.settings.settings["Enable PP counter"] = True

		cls.tests.append(getinfos("yomi"))
		cls.tests.append(getinfos("reimei", True))

	def testinfos(self):
		for i in range(len(self.tests)):
			case = self.tests[i]
			for x in range(len(case[1])):
				self.infotest(case, x)

	def infotest(self, case, x):
		resultinfo = checkmain(case[0], case[1][x], self.settings, True)
		components = FrameObjects()

		components.ppcounter = PPCounter(self.settings)
		updater = Updater(resultinfo, components, self.settings, case[1][x].mod_combination, case[0].path)

		for x in range(1, len(case[0].hitobjects)):
			updater.update(case[0].hitobjects[x]["time"])
			self.assertAlmostEqual(int(ezpp_pp(updater.ez)), int(components.ppcounter.pp), delta=2)


if __name__ == '__main__':
	unittest.main()
