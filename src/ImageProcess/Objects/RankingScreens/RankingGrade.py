from PIL import Image

from ....EEnum.EGrade import Grade
from ... import imageproc
from .ARankingScreen import ARankingScreen
from ....global_var import Settings


class RankingGrade(ARankingScreen):
	def __init__(self, replayinfo, gradeframes, gap):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy)

		self.grades = {10: Grade.SS, 9: Grade.S, 8: Grade.A, 7: Grade.B, 6: Grade.C, 5: Grade.D}

		total = replayinfo.number_300s + replayinfo.number_100s + replayinfo.number_50s + replayinfo.misses
		p300 = replayinfo.number_300s/total
		self.playergrade = max(5, int(p300 * 10)) - int(replayinfo.misses > 0)
		self.playergrade = max(5, self.playergrade)

		# Over 90% 300s, less than 1% 50s and no misses
		p50 = replayinfo.number_50s/total
		self.playergrade -= int(self.playergrade == 9 and p50 >= 0.01)

		self.gradeframe = gradeframes[self.grades[self.playergrade]]
		self.gap = int(gap * Settings.scale * 0.75)


	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			imageproc.add(self.gradeframe, background, Settings.width - 192 * Settings.scale, 320 * Settings.scale, self.alpha)
