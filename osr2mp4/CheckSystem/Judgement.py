import math
from osr2mp4.CheckSystem.HitObjects.HitObject import HitObject
from osr2mp4.CheckSystem.HitObjects.Slider import Slider
from osr2mp4.CheckSystem.HitObjects.Spinner import Spinner
from osr2mp4.osrparse.enums import Mod


class DiffCalculator:
	RELAX_BONUS_ACCEL = 4

	def __init__(self, diff):
		self.diff = diff
		self.max_distance = self.cs()
		self.slidermax_distance = self.max_distance * 2.4  # source: https://www.reddit.com/r/osugame/comments/9rki8o/how_are_slider_judgements_calculated/e8hwx85?utm_source=share&utm_medium=web2x
		self.score, self.scorewindow = self.od()
		self.time_preempt = self.ar()

	def cs(self):
		# source: https://www.reddit.com/r/osugame/comments/5gd3dm/whats_the_cspixel_formula/
		# this formula is closer to the real osu than the formula in the wiki
		return 23.05 - (self.diff["CircleSize"] - 7) * 4.4825  # 54.4 - 4.48 * self.diff["CircleSize"]

	def od(self):
		# source: https://github.com/ppy/osu/blob/4aafaab4494b721a72f30d4eab52326975e5bf4e/osu.Game.Rulesets.Osu/Scoring/OsuHitWindows.cs#L10
		# source1: https://github.com/ppy/osu/blob/7eaafe63cb36251b963b876f8f2436acb19f9cad/osu.Game/Beatmaps/BeatmapDifficulty.cs#L45
		# works better than osu wiki formula
		o = self.diff["OverallDifficulty"]
		scorewindow = [int(50 + 30 * (5 - o) / 5), int(100 + 40 * (5 - o) / 5), int(150 + 50 * (5 - o) / 5)]
		score = [300, 100, 50]
		return score, scorewindow

	def ar(self):
		# source: https://osu.ppy.sh/help/wiki/Beatmapping/Approach_rate
		a = self.diff["ApproachRate"]
		if a < 5:
			time_preempt = 1200 + 600 * (5 - a) / 5
		elif self.ar == 5:
			time_preempt = 1200
		else:
			time_preempt = 1200 - 750 * (a - 5) / 5
		return time_preempt

	def spinrequired(self, duration):
		# source: https://github.com/ppy/osu/blob/a8b137bb715db0c370148f04a548e7db6cc3cc9c/osu.Game.Rulesets.Osu/Objects/Spinner.cs#L33
		# TODO: use this source https://osu.ppy.sh/help/wiki/Beatmapping/Overall_difficulty
		multiplier = self.spinratio()

		return max(0, (duration-500)) / 1000 * multiplier

	def spinratio(self):
		od = self.diff["OverallDifficulty"]
		multiplier = 5
		if od > 5:
			multiplier = 5 + (7.5 - 5) * (od - 5) / 5
		if od < 5:
			multiplier = 5 - (5 - 3) * (5 - od) / 5
		return multiplier * 0.5

	def apply_mods_to_time(self, time, mods):
		return time


class Check:
	HEIGHT = 384
	WIDTH = 512
	SIXTY_FRAME_TIME = 1000/60

	def __init__(self, diff, hitobjects, mods):
		self.diff = DiffCalculator(diff)
		self.hitobjects = hitobjects
		self.index = 0

		self.mods = mods
		self.rxclick = False
		self.rxclickosr = None

		HitObject.diff = self.diff
		HitObject.mods = self.mods

		self.sliders_memory = {}
		self.spinners_memory = {}

	def checkcircle(self, index, replay, osrindex, clicked, combo):
		osr = replay[osrindex]

		if osrindex != self.rxclickosr:
			self.rxclick = False

		update_hitobj = False
		use_click = False
		score = None
		osu_d = self.hitobjects[index]
		time_difference = osr[3] - osu_d["time"]
		dist = math.sqrt((osr[0] - osu_d["x"]) ** 2 + (osr[1] - osu_d["y"]) ** 2)

		if "slider" in osu_d["type"] and osu_d["id"] not in self.sliders_memory:
			self.sliders_memory[osu_d["id"]] = Slider(self.hitobjects[index], combo)

		if Mod.Relax in self.mods:
			clicked = False  # disable key press
			if time_difference >= -11:  # relax hit note early source: https://osu.ppy.sh/community/forums/topics/122411
				clicked = True
				self.rxclick = True
				self.rxclickosr = osrindex

		if dist <= self.diff.max_distance and clicked:
			update_hitobj = True
			score = 0
			delta_time = abs(time_difference)
			use_click = True
			for x in range(3):
				if delta_time < self.diff.scorewindow[x]:
					score = self.diff.score[x]
					break
		else:
			if dist <= self.diff.max_distance and self.rxclick:
				# notelock
				update_hitobj = True
				score = None
				self.rxclick = False

			if time_difference > self.diff.scorewindow[2]:
				update_hitobj = True
				score = 0

		return update_hitobj, score, osu_d["time"], osu_d["id"], osu_d["x"], osu_d["y"], use_click, time_difference

	def checkslider(self, index, replay, osrindex):
		return self.sliders_memory[self.hitobjects[index]["id"]].check(replay, osrindex)

	def checkspinner(self, index, replay, osrindex):
		osu_d = self.hitobjects[index]
		if self.hitobjects[index]["id"] not in self.spinners_memory:
			self.spinners_memory[osu_d["id"]] = Spinner(osu_d)

		return self.spinners_memory[osu_d["id"]].check(replay, osrindex)
