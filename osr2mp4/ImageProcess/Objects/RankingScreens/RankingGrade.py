from PIL import Image
from osrparse.enums import Mod

from ....EEnum.EGrade import Grade
from ... import imageproc
from .ARankingScreen import ARankingScreen


class RankingGrade(ARankingScreen):
	def __init__(self, replayinfo, gradeframes, gap, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings)

		self.grades = {10: Grade.SS, 9: Grade.S, 8: Grade.A, 7: Grade.B, 6: Grade.C, 5: Grade.D}

		total = replayinfo.number_300s + replayinfo.number_100s + replayinfo.number_50s + replayinfo.misses
		p300 = replayinfo.number_300s/total
		self.playergrade = max(5, int(p300 * 10)) - int(replayinfo.misses > 0)
		self.playergrade = max(5, self.playergrade)

		# Over 90% 300s, less than 1% 50s and no misses
		p50 = replayinfo.number_50s/total
		self.playergrade -= int(self.playergrade == 9 and p50 >= 0.01)
		hd = int(Mod.Hidden in replayinfo.mod_combination)
		self.gradeframe = gradeframes[hd][self.grades[self.playergrade]]
		self.gap = int(gap * self.settings.scale * 0.75)


	def add_to_frame(self, background):
		# source: https://osu.ppy.sh/help/wiki/Skinning/Interface#ranking-grades
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			imageproc.add(self.gradeframe, background, self.settings.width - 192 * self.settings.scale, 320 * self.settings.scale, self.alpha)
