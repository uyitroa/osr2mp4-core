import math


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

	def cursorstate(self, clicked, osr):
		circle_clicked = False
		score = None

		osu_d = self.hitobjects[self.index]
		time_difference = osr[3] - osu_d["time"]
		dist = math.sqrt((osr[0] - osu_d["x"])**2 + (osr[1] - osu_d["y"])**2)
		if dist <= self.diff.max_distance and clicked:
			circle_clicked = True
			score = 0
			self.index += 1
			delta_time = abs(time_difference)

			for x in range(3):
				if delta_time < self.diff.scorewindow[x]:
					score = self.diff.score[x]
					break

		else:
			if time_difference > self.diff.scorewindow[2]:
				self.index += 1
				score = 0
		return circle_clicked, score, osu_d["x"], osu_d["y"]
