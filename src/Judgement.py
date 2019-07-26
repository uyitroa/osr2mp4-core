import math

from Curves.curve import Curve


class DiffCalculator:
	def __init__(self, diff):
		self.diff = diff
		self.max_distance = self.cs()
		self.slidermax_distance = self.max_distance * 3
		self.spinrequired, self.score, self.scorewindow = self.od()
		self.time_preempt = self.ar()

	def cs(self):
		return 54.4 - 4.48 * self.diff["CircleSize"]

	def od(self):
		o = self.diff["OverallDifficulty"]
		if o < 5:
			spins_per_second = 5 - 2 * (5 - o) / 5
		elif o == 5:
			spins_per_second = 5
		else:
			spins_per_second = 5 + 2.5 * (o - 5) / 5

		scorewindow = [50 + 30 * (5 - o) / 5, 100 + 40 * (5 - o) / 5,  150 + 50 * (5 - o) / 5]
		score = [300, 100, 50]
		return spins_per_second, score, scorewindow

	def ar(self):
		a = self.diff["ApproachRate"]
		if a < 5:
			time_preempt = 1200 + 600 * (5 - a) / 5
		elif self.ar == 5:
			time_preempt = 1200
		else:
			time_preempt = 1200 - 750 * (a - 5) / 5
		return time_preempt


class Check:
	def __init__(self, diff, hitobjects):
		self.diff = DiffCalculator(diff)
		self.hitobjects = hitobjects
		self.index = 0

		self.CIRCLE = 0
		self.SLIDER = 1

		self.circlesliderclicked = False
		self.repeatedslider = 1
		self.sliderfollow_prevstate = False
		self.score = 0

	def cursorstate(self, clicked, osr):
		if self.index >= len(self.hitobjects):
			return False, None, None, None, None, None, None
		osu_d = self.hitobjects[self.index]
		followappear = False
		if "circle" in osu_d["type"]:
			return (*self.checkcircle(osu_d, osr, clicked), followappear)

		elif "slider" in osu_d["type"]:
			return (*self.checkslider(osu_d, osr, clicked),)

		self.index += 1
		return False, None, None, None, None, None, None

	def checkcircle(self, osu_d, osr, clicked):
		update_hitobj = False
		score = None

		time_difference = osr[3] - osu_d["time"]
		dist = math.sqrt((osr[0] - osu_d["x"])**2 + (osr[1] - osu_d["y"])**2)
		if dist <= self.diff.max_distance and clicked:
			update_hitobj = True
			score = 0
			delta_time = abs(time_difference)

			for x in range(3):
				if delta_time <= self.diff.scorewindow[x]:
					score = self.diff.score[x]
					break
			if "circle" in osu_d["type"] or osr[3] > osu_d["end time"]:
				self.index += 1
				self.circlesliderclicked = False
				self.repeatedslider = 1
				self.sliderfollow_prevstate = False
				self.score = 0

		else:
			if time_difference > self.diff.scorewindow[2]:
				update_hitobj = True
				if "circle" in osu_d["type"] or osr[3] > osu_d["end time"]:
					self.index += 1
					self.circlesliderclicked = False
					self.repeatedslider = 1
					self.sliderfollow_prevstate = False
					self.score = 0
					score = 0

		return update_hitobj, score, osu_d["time"], osu_d["x"], osu_d["y"], self.CIRCLE

	def checkslider(self, osu_d, osr, clicked):
		followappear = False
		if osu_d["end time"] > osr[3] > osu_d["time"]:
			followappear = self.checkcursor_incurve(osu_d, osr)
		if osr[3] > osu_d["end time"]:
			self.index += 1
			self.circlesliderclicked = False
			self.repeatedslider = 1
			self.sliderfollow_prevstate = False
			score_toreturn = self.score
			self.score = 0
			return True, score_toreturn, osu_d["time"], osu_d["end x"], osu_d["end y"], self.SLIDER, followappear
		if not self.circlesliderclicked:
			return_tuple = self.checkcircle(osu_d, osr, clicked)
			if return_tuple[1] != 0 and return_tuple[1] is not None:
				self.score = 300
			self.circlesliderclicked = return_tuple[0]
			return return_tuple[0], None, osu_d["time"], 0, 0, self.CIRCLE, followappear
		elif followappear != self.sliderfollow_prevstate:
			self.sliderfollow_prevstate = followappear
			return True, None, osu_d["time"], 0, 0, self.SLIDER, followappear

		return False, None, None, None, None, None, None

	def checkcursor_incurve(self, osu_d, osr):
		slider_leniency = 36 if osu_d["duration"] > 72 else osu_d["duration"] / 2

		if (osr[3] - osu_d["time"]) / self.repeatedslider > osu_d["duration"]:
			self.repeatedslider += 1

		going_forward = self.repeatedslider % 2 == 1

		time_difference = (osr[3] - osu_d["time"]) / self.repeatedslider
		t = time_difference / osu_d["duration"]
		if not going_forward:
			t = 1 - t

		baiser = Curve.from_kind_and_points(osu_d["slider_type"], osu_d["ps"], osu_d["pixel_length"])
		pos = baiser(t)
		dist = math.sqrt((osr[0] - pos.x + osu_d["stacking"])**2 + (osr[1] - pos.y + osu_d["stacking"])**2)

		if dist <= self.diff.slidermax_distance and osr[2] != 0:
			if self.score == 0:
				self.score = 100
			return True
		elif osr[3] < osu_d["end time"] - slider_leniency:
			if self.score == 300:
				self.score = 100
			return False
