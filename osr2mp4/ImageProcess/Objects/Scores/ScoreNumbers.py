from PIL import Image

from ...PrepareFrames.YImage import YImage


class ScoreNumbers:
	def __init__(self, scale, settings):
		self.score_images = []
		scoreprefix = "-"
		score_x = scoreprefix + "x"
		score_percent = scoreprefix + "percent"
		score_dot = scoreprefix + "dot"
		for x in range(10):
			self.score_images.append(YImage(scoreprefix + str(x), settings, scale, prefix="ScorePrefix"))

		self.score_percent = YImage(score_percent, settings, scale, prefix="ScorePrefix")
		print(scale)
		# fierymod_v8_realest_ver[1] has very big score_percent.png but it doesn't show up in real osu
		# after some testing, if the image is >= 570px then it won't show up
		if self.score_percent.orig_cols >= int(570 * scale):
			self.score_percent.img = Image.new("RGBA", (self.score_percent.orig_cols, self.score_percent.orig_rows))

		self.score_dot = YImage(score_dot, settings, scale, prefix="ScorePrefix")

		self.score_x = YImage(score_x, settings, scale, prefix="ScorePrefix")

		self.combo_images = []
		for x in range(10):
			self.combo_images.append(YImage(scoreprefix + str(x), settings, scale, prefix="ComboPrefix"))
		self.combo_x = YImage(score_x, settings, scale, prefix="ComboPrefix")
