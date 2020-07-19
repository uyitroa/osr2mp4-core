from PIL import Image
from ....osrparse.enums import Mod

from ....CheckSystem.getgrade import getgrade
from ... import imageproc
from .ARankingScreen import ARankingScreen


class RankingGrade(ARankingScreen):
	def __init__(self, replayinfo, gradeframes, gap, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings)

		acc = {300: replayinfo.number_300s,
		       100: replayinfo.number_100s,
		       50: replayinfo.number_50s,
		       0: replayinfo.misses}
		grade = getgrade(acc)

		hd = int(Mod.Hidden in replayinfo.mod_combination)
		self.gradeframe = gradeframes[hd][grade]
		self.gap = int(gap * self.settings.scale * 0.75)

		if self.settings.skin_ini.general["Version"] == 1:
			self.y = 272
		else:
			self.y = 320

	def add_to_frame(self, background):
		# source: https://osu.ppy.sh/help/wiki/Skinning/Interface#ranking-grades
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			imageproc.add(self.gradeframe, background, self.settings.width - 192 * self.settings.scale,
			              self.y * self.settings.scale, self.alpha)
