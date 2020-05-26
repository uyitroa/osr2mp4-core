import cv2
from PIL import Image

from ImageProcess import imageproc
from ImageProcess.Objects.RankingScreens.ARankingScreen import ARankingScreen
from global_var import Settings


class RankingTitle(ARankingScreen):
	def __init__(self, frames, replayinfo, beatmap):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy)
		self.replayinfo = replayinfo
		self.artist = beatmap.meta["Artist"]
		self.beatmapname = beatmap.meta["Title"]
		self.mapper = beatmap.meta["Creator"]
		self.diff = beatmap.meta["Version"]
		self.player = replayinfo.player_name
		self.date = str(replayinfo.timestamp)
		self.date = self.date.replace("-", "/")

		self.rankingtitle = frames[0]

	def drawname(self, background, x_offset, y_offset, text, alpha, size):
		cv2.putText(background, text, (int(x_offset), int(y_offset)), cv2.QT_FONT_NORMAL, Settings.scale * size, (alpha * 255, alpha * 255, alpha * 255, alpha * 150), 1, cv2.LINE_AA)

	def add_to_frame(self, background, np_img):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.drawname(np_img, 0, 30 * Settings.scale, "{} - {} [{}]".format(self.artist, self.beatmapname, self.diff), self.alpha, 0.75)
			self.drawname(np_img, 0, 50 * Settings.scale, "Beatmap by {}".format(self.mapper), self.alpha, 0.5)
			self.drawname(np_img, 0, 70 * Settings.scale, "Played by {} on {}".format(self.player, self.date), self.alpha, 0.5)

			imageproc.add(self.rankingtitle, background, Settings.width - 32 * Settings.scale - self.rankingtitle.size[0], 10 * Settings.scale, self.alpha, topleft=True)
