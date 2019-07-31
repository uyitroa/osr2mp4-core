import math
import numpy as np
from Curves.curve import Curve


class DiffCalculator:
	def __init__(self, diff):
		self.diff = diff
		self.max_distance = self.cs()
		self.slidermax_distance = self.max_distance * 2.4
		self.score, self.scorewindow = self.od()
		self.time_preempt = self.ar()

	def cs(self):
		return 54.4 - 4.48 * self.diff["CircleSize"]

	def od(self):
		o = self.diff["OverallDifficulty"]
		scorewindow = [int(50 + 30 * (5 - o) / 5), int(100 + 40 * (5 - o) / 5), int(150 + 50 * (5 - o) / 5)]
		score = [300, 100, 50]
		return score, scorewindow

	def ar(self):
		a = self.diff["ApproachRate"]
		if a < 5:
			time_preempt = 1200 + 600 * (5 - a) / 5
		elif self.ar == 5:
			time_preempt = 1200
		else:
			time_preempt = 1200 - 750 * (a - 5) / 5
		return time_preempt

	def spinrequired(self, duration):
		od = self.diff["OverallDifficulty"]
		multiplier = 5
		if od > 5:
			multiplier = 5 + (7.5 - 5) * (od - 5) / 5
		if od < 5:
			multiplier = 5 - (5 - 3) * (5 - od) / 5
		multiplier *= 0.6
		return max(1, round(duration * multiplier / 1000 / 0.9))


class Check:
	def __init__(self, diff, hitobjects):
		self.diff = DiffCalculator(diff)
		self.hitobjects = hitobjects
		self.index = 0
		self.height = 384
		self.width = 512

		self.sliders_memory = {}
		self.spinners_memory = {}

	def checkcircle(self, index, replay, osrindex, clicked):
		osr = replay[osrindex]
		update_hitobj = False
		score = None
		osu_d = self.hitobjects[index]
		time_difference = osr[3] - osu_d["time"]
		dist = math.sqrt((osr[0] - osu_d["x"]) ** 2 + (osr[1] - osu_d["y"]) ** 2)
		if dist <= self.diff.max_distance and clicked:
			update_hitobj = True
			score = 0
			delta_time = abs(time_difference)

			for x in range(3):
				if delta_time < self.diff.scorewindow[x]:
					score = self.diff.score[x]
					break

		else:
			if time_difference > self.diff.scorewindow[2]:
				update_hitobj = True
				score = 0

		if "slider" in osu_d["type"]:
			self.sliders_memory[osu_d["time"]] = {"score": 300 if score != 0 else 0, "follow state": 0,
			                                      "repeated slider": 1,
			                                      "repeat checked": 0, "ticks index": 0, "done": False}

		return update_hitobj, score, osu_d["time"], osu_d["x"], osu_d["y"]

	def checkslider(self, index, replay, osrindex):
		osr = replay[osrindex]
		osu_d = self.hitobjects[index]
		if osu_d["time"] not in self.sliders_memory:
			self.sliders_memory[osu_d["time"]] = {"score": 0, "follow state": 0, "repeated slider": 1,
			                                      "repeat checked": 0,
			                                      "ticks index": 0, "done": False}
		slider_d = self.sliders_memory[osu_d["time"]]
		followappear = False
		hitvalue = combostatus = 0
		prev_state = slider_d["follow state"]
		if osu_d["end time"] > osr[3] > osu_d["time"]:
			followappear, hitvalue, combostatus = self.checkcursor_incurve(osu_d, replay, osrindex, slider_d)

		if osr[3] > osu_d["end time"]:
			return True, slider_d["score"], osu_d["time"], osu_d["end x"], osu_d["end y"], \
			       False, hitvalue, combostatus

		if followappear != prev_state:
			slider_d["follow state"] = followappear
			return True, None, osu_d["time"], 0, 0, followappear, hitvalue, combostatus

		return False, None, None, None, None, None, hitvalue, combostatus

	def checkcursor_incurve(self, osu_d, replay, osr_index, slider_d):
		osr = replay[osr_index]
		if slider_d["done"]:
			return False, 0, 0

		if (osr[3] - osu_d["time"]) / slider_d["repeated slider"] > osu_d["duration"]:
			slider_d["repeated slider"] = math.ceil((osr[3] - osu_d["time"]) / osu_d["duration"])

		going_forward = slider_d["repeated slider"] % 2 == 1

		time_difference = (osr[3] - osu_d["time"]) / slider_d["repeated slider"]


		slider_leniency = min(36, osu_d["duration"] / 2)
		hasendtick = time_difference > osu_d["duration"] - slider_leniency
		hasendtick = hasendtick and slider_d["repeat checked"] < slider_d["repeated slider"]
		if hasendtick:
			t = (osu_d["duration"] - slider_leniency)/osu_d["duration"]
		else:
			t = time_difference / osu_d["duration"]
		if not going_forward:
			t = 1 - t

		hastick, tickadd, t = self.tickover(going_forward, t, osu_d, slider_d)
		slider_d["ticks index"] += tickadd

		hasreverse = slider_d["repeated slider"] < osu_d["repeated"]

		baiser = Curve.from_kind_and_points(osu_d["slider type"], osu_d["ps"], osu_d["pixel length"])
		pos = baiser(t)
		dist = math.sqrt((osr[0] - pos.x + osu_d["stacking"]) ** 2 + (osr[1] - pos.y + osu_d["stacking"]) ** 2)
		in_ball = dist <= self.diff.slidermax_distance and osr[2] != 0

		posr = replay[osr_index-1]
		pos = baiser(t)
		prevdist = math.sqrt((posr[0] - pos.x + osu_d["stacking"]) ** 2 + (posr[1] - pos.y + osu_d["stacking"]) ** 2)
		prev_inball = prevdist <= self.diff.slidermax_distance and posr[2] != 0
		touchtick = hastick and prev_inball
		touchend = hasendtick and prev_inball

		if touchtick == touchend and touchend:
			print("true fuck")

		if touchtick or touchend:
			slider_d["score"] = max(slider_d["score"], 100)
			hitvalue = touchtick * 10
			hitvalue += touchend * 30
			hitvalue *= not slider_d["done"]
			slider_d["done"] = touchend and not hasreverse
			slider_d["repeat checked"] += touchend or touchtick
			return in_ball, hitvalue, int(touchend or touchtick)

		if (hastick and not touchtick) or (hasendtick and not touchend):
			slider_d["score"] = min(slider_d["score"], 100)
		slider_d["repeat checked"] += hasendtick and hasreverse and not touchend
		slider_d["done"] = hasendtick and not touchend and not hasreverse
		return in_ball, 0, -((hastick and not touchtick) or (hasendtick and hasreverse and not touchend))


	def tickover(self, goingforward, t, osu_d, slider_d):
		repeat = osu_d["repeated"] - slider_d["repeated slider"] > 0
		ticks_index = slider_d["ticks index"]
		if ticks_index < 0:
			return False, 1 * repeat, t
		if ticks_index >= len(osu_d["slider ticks"]):
			return False, -1 * repeat, t

		if goingforward:
			if t > osu_d["slider ticks"][ticks_index]:
				return True, 1, osu_d["slider ticks"][ticks_index]
			else:
				return False, 0
		if t < osu_d["slider ticks"][ticks_index]:
			return True, -1, osu_d["slider ticks"][ticks_index]
		return False, 0, t

	def checkspinner(self, index, osr):
		osu_d = self.hitobjects[index]
		if osr[3] < osu_d["time"]:
			return False, None, None, None, 0, 0

		if osr[3] >= osu_d["end time"]:
			spin_d = self.spinners_memory[osu_d["time"]]
			progress = spin_d["progress"] / 360 / self.diff.spinrequired(osu_d["end time"] - osu_d["time"])
			print(progress)
			if progress > 1:
				hitresult = 300
			elif progress > 0.9:
				hitresult = 100
			elif progress > 0.5:
				hitresult = 100
			elif progress > 0.1:
				hitresult = 50
			else:
				hitresult = 0
			return True, spin_d["cur rotation"], progress, hitresult, 0, 0

		spinning = osr[2] != 0
		angle = -np.rad2deg(np.arctan2(osr[1] - self.height / 2, osr[0] - self.width / 2))

		if osu_d["time"] not in self.spinners_memory:
			self.spinners_memory[osu_d["time"]] = {"angle": angle, "spinning": spinning, "cur rotation": 0,
			                                       "progress": 0, "extra": 0}

		spin_d = self.spinners_memory[osu_d["time"]]
		if not spin_d["spinning"] and spinning:
			spin_d["angle"] = angle
		spin_d["spinning"] = spinning

		lastangle = spin_d["angle"]
		if angle - lastangle > 180:
			lastangle += 360
		elif lastangle - angle > 180:
			lastangle -= 360

		spin_d["cur rotation"] += angle - lastangle
		if spin_d["cur rotation"] > 360:
			spin_d["cur rotation"] -= 360
		spin_d["progress"] += abs(angle - lastangle)
		spin_d["extra"] += abs(angle - lastangle)
		spin_d["angle"] = angle
		progress = spin_d["progress"] / 360 / self.diff.spinrequired(osu_d["end time"] - osu_d["time"])

		bonus = int(spin_d["progress"] / 360 - self.diff.spinrequired(osu_d["end time"] - osu_d["time"]))
		bonus = max(0, bonus)

		hitvalue = 0
		if spin_d["extra"] >= 360 and progress <= 1:
			spin_d["extra"] -= 360
			hitvalue = 100

		return spinning, spin_d["cur rotation"], progress, None, bonus, hitvalue
