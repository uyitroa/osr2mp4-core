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

		self.sliders_memory = {}


	def checkcircle(self, index, osr, clicked):
		update_hitobj = False
		score = None
		osu_d = self.hitobjects[index]
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

		else:
			if time_difference > self.diff.scorewindow[2]:
				update_hitobj = True
				score = 0

		if "slider" in osu_d["type"]:
			self.sliders_memory[osu_d["time"]] = {"score": 300 if score != 0 else 0, "follow state": 0, "repeated slider": 1}

		return update_hitobj, score, osu_d["time"], osu_d["x"], osu_d["y"]

	def checkslider(self, index, osr):
		osu_d = self.hitobjects[index]
		if osu_d["time"] not in self.sliders_memory:
			self.sliders_memory[osu_d["time"]] = {"score": 0, "follow state": 0, "repeated slider": 1}

		followappear = False
		if osu_d["end time"] > osr[3] > osu_d["time"]:
			followappear = self.checkcursor_incurve(osu_d, osr)
		if osr[3] > osu_d["end time"]:
			score = self.sliders_memory[osu_d["time"]]["score"]
			del self.sliders_memory[osu_d["time"]]
			return True, score, osu_d["time"], osu_d["end x"], osu_d["end y"], followappear

		if followappear != self.sliders_memory[osu_d["time"]]["follow state"]:
			self.sliders_memory[osu_d["time"]]["follow state"] = followappear
			return True, None, osu_d["time"], 0, 0, followappear

		return False, None, None, None, None, None

	def checkcursor_incurve(self, osu_d, osr):
		slider_leniency = 36 if osu_d["duration"] > 72 else osu_d["duration"] / 2

		if (osr[3] - osu_d["time"]) / self.sliders_memory[osu_d["time"]]["repeated slider"] > osu_d["duration"]:
			self.sliders_memory[osu_d["time"]]["repeated slider"] += 1

		going_forward = self.sliders_memory[osu_d["time"]]["repeated slider"] % 2 == 1

		time_difference = (osr[3] - osu_d["time"]) / self.sliders_memory[osu_d["time"]]["repeated slider"]
		t = time_difference / osu_d["duration"]
		if not going_forward:
			t = 1 - t

		baiser = Curve.from_kind_and_points(osu_d["slider_type"], osu_d["ps"], osu_d["pixel_length"])
		pos = baiser(t)
		dist = math.sqrt((osr[0] - pos.x + osu_d["stacking"])**2 + (osr[1] - pos.y + osu_d["stacking"])**2)

		if dist <= self.diff.slidermax_distance and osr[2] != 0:
			if self.sliders_memory[osu_d["time"]]["score"] == 0:
				self.sliders_memory[osu_d["time"]]["score"] = 100
			return True
		elif osr[3] < osu_d["end time"] - slider_leniency:
			if self.sliders_memory[osu_d["time"]]["score"] == 300:
				self.sliders_memory[osu_d["time"]]["score"] = 100
			return False

	def checkspinner(self, osu_d, osr):
		pass