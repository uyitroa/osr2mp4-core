# from datetime import datetime, timedelta
import time

from PIL import Image
# from dateutil.relativedelta import relativedelta
# from pytz import timezone

from ... import imageproc
from .ARankingScreen import ARankingScreen
from ...PrepareFrames.Components.Text import prepare_text


class RankingTitle(ARankingScreen):
	def __init__(self, frames, replayinfo, beatmap, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings=settings)
		self.replayinfo = replayinfo
		self.artist = beatmap.meta["Artist"]
		self.beatmapname = beatmap.meta["Title"]
		self.mapper = beatmap.meta["Creator"]
		self.diff = beatmap.meta["Version"]
		self.player = replayinfo.player_name

		timestamp = self.set_timezone(replayinfo)
		self.date = str(timestamp.replace(microsecond=0))
		self.date = self.date.replace("-", "/")

		self.rankingtitle = frames[0]

		titleimg = prepare_text(["{} - {} [{}]".format(self.artist, self.beatmapname, self.diff)], 30 * self.settings.scale, (255, 255, 255, 255), settings)
		creatorimg = prepare_text(["Beatmap by {}".format(self.mapper)], 20 * self.settings.scale, (255, 255, 255, 255), settings)
		playerimg = prepare_text(["Played by {} on {}".format(self.player, self.date)], 20 * self.settings.scale, (255, 255, 255, 255), settings)

		self.textimgs = {**titleimg, **creatorimg, **playerimg}

	def set_timezone(self, replayinfo):
		return replayinfo.timestamp
		# timestamp = replayinfo.timestamp
		# utcnow = timezone('utc').localize(datetime.utcnow())
		# mm = time.tzname[0]
		# here = utcnow.astimezone(timezone(mm)).replace(tzinfo=None)
		# there = utcnow.astimezone(timezone('utc')).replace(tzinfo=None)
		# offset = relativedelta(here, there).hours
		# timestamp += timedelta(hours=offset)
		# return timestamp

	def drawname(self, background, x_offset, y_offset, text, alpha, size):
		imageproc.add(self.textimgs[text], background, x_offset, y_offset, alpha=alpha, topleft=True)

	def add_to_frame(self, background, np_img):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:
			self.drawname(background, 0, 0 * self.settings.scale, "{} - {} [{}]".format(self.artist, self.beatmapname, self.diff), self.alpha, 0.75)
			self.drawname(background, 0, 35 * self.settings.scale, "Beatmap by {}".format(self.mapper), self.alpha, 0.5)
			self.drawname(background, 0, 60 * self.settings.scale, "Played by {} on {}".format(self.player, self.date), self.alpha, 0.5)

			# source: https://osu.ppy.sh/help/wiki/Skinning/Interface#ranking-screen
			imageproc.add(self.rankingtitle, background, self.settings.width - 32 * self.settings.scale - self.rankingtitle.size[0], 0, self.alpha, topleft=True)
