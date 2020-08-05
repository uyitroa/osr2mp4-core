import logging
import math
import numpy as np
from ..osrparse.enums import Mod

from ..EEnum.EReplay import Replays


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
			self.sliders_memory[osu_d["id"]] = {"score": 0, "max score": 1, "follow state": 0,
			                                    "repeated slider": 1, "repeat checked": 0, "ticks index": 0,
			                                    "done": False,
			                                    "dist": self.diff.max_distance, "last osr index": -1, "tickend": 0,
			                                    "combo": combo}

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
		osr = replay[osrindex]
		osu_d = self.hitobjects[index]

		slider_d = self.sliders_memory[osu_d["id"]]

		hitvalue = combostatus = 0
		followappear = prev_state = slider_d["follow state"]

		if osu_d["end time"] > osr[3] > osu_d["time"]:
			if slider_d["last osr index"] == -1:
				slider_d["last osr index"] = osrindex - 1
			followappear, hitvalue, combostatus = self.checkcursor_incurve(osu_d, replay, osrindex, slider_d)
		elif osu_d["time"] - self.diff.score[2]/2 < osr[3] <= osu_d["time"]:
			pos = osu_d["slider_c"].at(0)
			in_ball = self.cursor_inslider(slider_d, replay, osrindex, pos)
			if in_ball:
				slider_d["dist"] = self.diff.slidermax_distance
			else:
				slider_d["dist"] - self.diff.max_distance

		updatefollow = followappear != slider_d["follow state"]

		if osr[3] > osu_d["end time"]:
			if slider_d["score"] == 0:
				hitresult = 0
			elif slider_d["score"] < slider_d["max score"] / 2:
				hitresult = 50
			elif slider_d["score"] < slider_d["max score"]:
				hitresult = 100
			elif slider_d["score"] == slider_d["max score"]:
				hitresult = 300
			else:
				hitresult = 300
				logging.warning("what {} {}".format(slider_d["score"], slider_d["max score"]))

			return True, hitresult, osu_d["time"], osu_d["id"], osu_d["end x"], osu_d["end y"], \
			       False, hitvalue, combostatus, slider_d["tickend"], True

		if followappear != prev_state or hitvalue != 0:
			slider_d["follow state"] = followappear
			return True, None, osu_d["time"], osu_d["id"], 0, 0, followappear, hitvalue, combostatus, 0, updatefollow

		return False, None, osu_d["time"], osu_d["id"], osu_d["end x"], osu_d["end y"], followappear, hitvalue, combostatus, 0, False

	def cursor_inslider(self, slider_d, replay, osr_index, pos):
		osr_index = max(0, min(len(replay)-1, osr_index))
		rep = replay[osr_index]
		dist = (rep[Replays.CURSOR_X] - pos[0]) ** 2 + (rep[Replays.CURSOR_Y] - pos[1]) ** 2

		clicked = rep[Replays.KEYS_PRESSED] != 0
		if Mod.Relax in self.mods:
			clicked = True

		return dist <= slider_d["dist"]**2 and clicked

	def aaa(self, replay, osr_index, pos):
		osr_index = max(0, min(len(replay)-1, osr_index))
		rep = replay[osr_index]
		return math.sqrt((rep[Replays.CURSOR_X] - pos[0]) ** 2 + (rep[Replays.CURSOR_Y] - pos[1]) ** 2)

	def closestreplay(self, replay, index, curtime):
		prev_index = max(0, index - 1)
		prevtime = abs(round(replay[prev_index][3]) - curtime)
		ctime = abs(round(replay[index][3]) - curtime)
		if prevtime >= ctime:
			return 0
		else:
			return -1

	def checkcursor_incurve(self, osu_d, replay, osr_index, slider_d):

		osr = replay[osr_index]

		if slider_d["done"]:
			return slider_d["follow state"], 0, 0

		hasreversetick = False
		cur_repeated = math.ceil((osr[3] - osu_d["time"]) / osu_d["duration"])
		if cur_repeated > slider_d["repeated slider"]:
			hasreversetick = osu_d["repeated"] != slider_d["repeated slider"]

		going_forward = cur_repeated % 2 == 1

		# source: https://www.reddit.com/r/osugame/comments/9rki8o/how_are_slider_judgements_calculated/e8hwx85?utm_source=share&utm_medium=web2x
		slider_leniency = min(36, (osu_d["duration"] * osu_d["repeated"]) / 2)

		hasendtick = osr[3] >= int(osu_d['end time'] - slider_leniency)
		hasendtick = hasendtick and not slider_d["tickend"]

		# if hasendtick:
		# 	osr_index += self.closestreplay(replay, osr_index, int(osu_d["end time"]) - slider_leniency)

		delta_time = (osr[3] - osu_d["time"]) % osu_d["duration"]
		if not going_forward:
			delta_time = osu_d["duration"] - delta_time
		dist = osu_d["pixel length"] / osu_d["duration"] * delta_time

		slider_c = osu_d["slider_c"]
		pos = slider_c.at(dist)

		hastick, tickadd, tickt = self.tickover(dist/osu_d["pixel length"], osu_d, slider_d, hasreversetick)
		slider_d["ticks index"] += tickadd

		tick_inball = self.cursor_inslider(slider_d, replay, osr_index, pos)

		# if osu_d["time"] == 307397:
		# if osu_d["time"] == 23065:
		# 	print(self.diff.slidermax_distance, self.diff.max_distance)
		# 	print(self.aaa(replay, osr_index, pos), self.aaa(replay, osr_index-1, pos), self.aaa(replay, osr_index+1, pos))
		# 	print(f"osr: {osr}\nosr -1: {replay[osr_index-1]}\nosr +1: {replay[osr_index+1]}\nosu id {osu_d['time']} osu endtick: {osu_d['end time'] - slider_leniency} pos: {pos} endtick: {hasendtick} inball: {tick_inball} duration {osu_d['duration']}\n\n")

		in_ball = tick_inball
		if in_ball:
			slider_d["dist"] = self.diff.slidermax_distance
		else:
			slider_d["dist"] = self.diff.max_distance

		slider_d["last osr index"] = osr_index

		touchtick = hastick and tick_inball
		touchend = hasendtick and tick_inball
		touchreverse = hasreversetick and tick_inball

		slider_d["max score"] += hastick + hasendtick + hasreversetick

		slider_d["done"] = osr[3] + slider_leniency >= int(osu_d["end time"]) and osu_d["repeated"] == slider_d["repeated slider"]
		slider_d["repeat checked"] += hasendtick or (int(hasreversetick) * (cur_repeated - slider_d["repeated slider"]))
		slider_d["repeated slider"] = cur_repeated
		# slider_c.update(t, dist)

		if touchtick or touchend or touchreverse:
			hitvalue = touchtick * 10
			hitvalue += (touchend + touchreverse) * 30
			slider_d["tickend"] = touchend or slider_d["tickend"]
			# hitvalue *= not slider_d["done"]
			slider_d["score"] += touchtick + touchend + touchreverse
			# touchend and touchreverse can be true both same time in case slider is too fast
			return in_ball, hitvalue, touchend + touchtick + touchreverse

		return in_ball, 0, -((hastick and not touchtick) or (hasreversetick and not touchreverse))

	def tickover(self, t, osu_d, slider_d, reverse):
		goingforward = slider_d["repeated slider"] % 2 == 1

		ticks_index = slider_d["ticks index"]
		if ticks_index < 0:
			return False, 1 * reverse, t
		if ticks_index >= len(osu_d["slider ticks"]):
			return False, -1 * reverse, t

		if goingforward:
			if t > osu_d["slider ticks"][ticks_index]:
				return True, 1, osu_d["slider ticks"][ticks_index]
			else:
				return False, 0, t
		if t < osu_d["slider ticks"][ticks_index]:
			return True, -1, osu_d["slider ticks"][ticks_index]
		return False, 0, t

	def checkspinner(self, index, replay, osrindex):
		osr = replay[osrindex]
		osu_d = self.hitobjects[index]

		if osr[Replays.TIMES] < osu_d["time"]:
			return False, None, None, None, 0, 0, 0

		if osu_d["id"] not in self.spinners_memory:
			self.spinners_memory[osu_d["id"]] = {"rpm": 0, "cur speed": 0, "theoretical speed": 0, "prev angle": 0,
												"frame variance": 0, "rot count": 0}
			timediff = self.SIXTY_FRAME_TIME
		else:
			timediff = osr[Replays.TIMES] - replay[max(0, osrindex-1)][Replays.TIMES]

		if osr[Replays.TIMES] >= osu_d["end time"]:
			spinner = self.spinners_memory[osu_d["id"]]
			rotation = (spinner["rot count"] % 1) * 360
			spinrequired = self.diff.spinrequired(osu_d["end time"] - osu_d["time"])
			progress = spinner["rot count"] / max(1, spinrequired)  # avoid divsion by 0 using max(1, spinrequired)

			if spinner["rot count"] > spinrequired + 1 or Mod.SpunOut in self.mods:
				hitresult = 300
			elif spinner["rot count"] > spinrequired:
				hitresult = 100
			elif spinner["rot count"] >= 0.1 * spinrequired:
				hitresult = 50
			else:
				hitresult = 0

			return True, rotation, progress, hitresult, 0, 0, spinner["rpm"]

		duration = osu_d["end time"] - osu_d["time"]
		max_accel = 0.00008 + max(0, (5000 - duration) / 1000 / 2000)

		spinner = self.spinners_memory[osu_d["id"]]

		elapsedtime = timediff  # osr[Replays.TIMES] - replay[max(0, osrindex-1)][Replays.TIMES]

		cursor_vector_x = osr[Replays.CURSOR_X] - self.WIDTH/2
		cursor_vector_y = osr[Replays.CURSOR_Y] - self.HEIGHT/2
		cursor_angle = math.atan2(cursor_vector_y, cursor_vector_x)
		anglediff = cursor_angle - spinner["prev angle"]

		if cursor_angle - spinner["prev angle"] < -math.pi:
			anglediff = (2 * math.pi) + cursor_angle - spinner["prev angle"]
		elif spinner["prev angle"] - cursor_angle < -math.pi:
			anglediff = (-2 * math.pi) - spinner["prev angle"] + cursor_angle

		decay = math.pow(0.999, timediff)
		spinner["frame variance"] = decay * spinner["frame variance"] + (1 - decay) * timediff

		if anglediff == 0:
			spinner["theoretical speed"] /= 3
		else:
			if Mod.Relax not in self.mods and osr[Replays.KEYS_PRESSED] == 0:
				# print(osr[Replays.TIMES])
				anglediff = 0

			if abs(anglediff) < math.pi:
				# commented this block because it breaks spunout and auto mods
				# if self.diff.apply_mods_to_time(timediff, self.mods) > self.SIXTY_FRAME_TIME * 1.04:
				# 	spinner["theoretical speed"] = anglediff / self.diff.apply_mods_to_time(timediff, self.mods)
				# else:
				spinner["theoretical speed"] = anglediff / self.SIXTY_FRAME_TIME
			else:
				spinner["theoretical speed"] = 0

		spinner["prev angle"] = cursor_angle

		max_accel_this_frame = self.diff.apply_mods_to_time(max_accel * elapsedtime, self.mods)

		if Mod.SpunOut in self.mods:
			spinner["cur speed"] = 0.03
		elif spinner["theoretical speed"] > spinner["cur speed"]:
			if spinner["cur speed"] < 0 and Mod.Relax in self.mods:
				max_accel_this_frame /= self.diff.RELAX_BONUS_ACCEL

			spinner["cur speed"] += min(spinner["theoretical speed"] - spinner["cur speed"], max_accel_this_frame)
		else:
			if spinner["cur speed"] > 0 and Mod.Relax in self.mods:
				max_accel_this_frame /= self.diff.RELAX_BONUS_ACCEL

			spinner["cur speed"] += max(spinner["theoretical speed"] - spinner["cur speed"], -max_accel_this_frame)

		spinner["cur speed"] = max(-0.05, min(spinner["cur speed"], 0.05))

		decay = math.pow(0.9, elapsedtime / self.SIXTY_FRAME_TIME)
		rpm = spinner["rpm"] * decay + (1.0 - decay) * (abs(spinner["cur speed"]) * 1000) / (math.pi * 2) * 60
		spinner["rpm"] = rpm

		prevcount = spinner["rot count"]
		spinner["rot count"] += rpm * timediff / 60000

		direction = -1 if spinner["cur speed"] >= 0 else 1
		rotation = (spinner["rot count"] * 360) % 360 * direction
		spinrequired = self.diff.spinrequired(duration)
		progress = spinner["rot count"] / max(1, spinrequired)  # avoid divsion by 0 using max(1, spinrequired)
		bonus = max(0, int(spinner["rot count"] - spinrequired - 3))

		rot_increased = int(spinner["rot count"]) > int(prevcount)
		hitvalue = (spinner["rot count"] > 1 and rot_increased and int(spinner["rot count"]) % 2 == 0) * 100

		return True, rotation, progress, None, bonus, hitvalue, rpm

