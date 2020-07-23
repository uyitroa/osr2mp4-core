import os
import unittest

import osr2mp4

from osr2mp4.ImageProcess.PrepareFrames.Components.Cursor import prepare_cursor, prepare_cursormiddle

from osr2mp4.Parser.skinparser import Skin

from osr2mp4.global_var import Settings

from osr2mp4.EEnum.EImageFrom import ImageFrom

from osr2mp4.ImageProcess.PrepareFrames.YImage import YImages

from utils import abspath


class LoadSkinTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.settings = Settings()
		cls.settings.skin_ini = Skin("", "", inipath=os.path.join(abspath, "skininis/skin.ini"))
		cls.settings.default_skin_ini = cls.settings.skin_ini

	def testloadskin(self):
		self.settings.skin_path = os.path.join(abspath, "skintests/Hank Hill")
		a = YImages("scorebar-colour", self.settings, delimiter="-")
		self.assertEqual(a.imgfrom, ImageFrom.SKIN_X2, msg=f"Expect loading scorebar-colour@2.png from {self.settings.skin_path}")
		self.assertEqual(len(a.frames), 1, msg=f"Expect loading scorebar-colour@2.png from {self.settings.skin_path}")

		self.settings.skin_path = os.path.join(abspath, "shige copy")
		a = YImages("followpoint", self.settings, delimiter="-", rotate=True)
		self.assertEqual(a.imgfrom, ImageFrom.SKIN_X, msg=f"Expect loading 8 followpoint-x.png from {self.settings.skin_path}")
		self.assertEqual(len(a.frames), 8, msg=f"Expect loading 8 followpoint-x.png from {self.settings.skin_path}")

		a = YImages("score", self.settings, delimiter="-", rotate=True)
		self.assertEqual(a.imgfrom, ImageFrom.SKIN_X2, msg=f"Expect loading 10 score-x@2x.png from {self.settings.skin_path}")
		self.assertEqual(len(a.frames), 10, msg=f"Expect loading 8 followpoint-x.png from {self.settings.skin_path}")

	def testloadcursor(self):
		self.settings.skin_path = os.path.join(abspath, "shige copy")
		cursor, default = prepare_cursor(1, self.settings)
		cursormiddle, continuous = prepare_cursormiddle(1, self.settings, default)
		self.assertEqual(default, False, msg=f"Expect not using default cursor {self.settings.skin_path}")
		self.assertEqual(continuous, True, msg=f"Expect using continuous cursortrail {self.settings.skin_path}")

		self.settings.skin_path = os.path.join(abspath, "skintests/Hank Hill")
		self.settings.default_path = os.path.join(os.path.dirname(osr2mp4.__file__), "res/default")
		cursor, default = prepare_cursor(1, self.settings)
		cursormiddle, continuous = prepare_cursormiddle(1, self.settings, default)
		self.assertEqual(default, True, msg=f"Expect using default cursor {self.settings.skin_path}")
		self.assertEqual(continuous, True,  msg=f"Expect using continuous cursortrail {self.settings.skin_path}")



if __name__ == '__main__':
	unittest.main()
