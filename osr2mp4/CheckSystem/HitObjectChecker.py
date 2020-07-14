import logging
import math

from ..osrparse.replay import Replay

from ..osrparse.enums import Mod

from ..EEnum.EReplay import Replays
from .Health import HealthProcessor, HealthDummy
from .Judgement import Check
from collections import namedtuple
import copy
from ..EEnum.EState import States


Info = namedtuple("Info", "time combo combostatus showscore score accuracy clicks hitresult timestamp id hp maxcombo more")
Circle = namedtuple("Circle", "state deltat followstate sliderhead x y")
Slider = namedtuple("Slider", "followstate hitvalue tickend x y end arrowindex")
Spinner = namedtuple("Spinner", "rotate progress bonusscore hitvalue")


def difficulty_multiplier(diff):
	points = int(diff["BaseOverallDifficulty"] + diff["BaseHPDrainRate"] + diff["BaseCircleSize"] - 0.25)
	# points -= int(self.diff["BaseApproachRate"] + 1)  # math.ceil but cooler
	if points in range(0, 6):
		return 2
	if points in range(6, 13):
		return 3
	if points in range(13, 18):
		return 4
	if points in range(18, 25):
		return 5
	return 6


def getmultiplier(mods):
	multiplier = {Mod.Easy: 0.5, Mod.NoFail: 0.5, Mod.HalfTime: 0.3,
	              Mod.HardRock: 1.06, Mod.NoVideo: 1, Mod.SuddenDeath: 1, Mod.Perfect: 1, Mod.DoubleTime: 1.12, Mod.Nightcore: 1.12, Mod.Hidden: 1.06, Mod.Flashlight: 1.12,
	              Mod.Relax: 0, Mod.Autopilot: 0, Mod.SpunOut: 0.9, Mod.Autoplay: 1, Mod.NoMod: 1, Mod.ScoreV2: 1}
	result = 1
	for m in mods:
		result *= multiplier[m]
	return result


class HitObjectChecker:
	def __init__(self, beatmap, settings, replay: Replay, tests=False):
		self.diff = beatmap.diff
		self.settings = settings
		self.hitobjects = copy.deepcopy(beatmap.hitobjects)
		self.diff_multiplier = self.difficulty_multiplier()
		if self.diff["ApproachRate"] < 5:
			self.time_preempt = 1200 + 600 * (5 - self.diff["ApproachRate"]) / 5
			self.fade_in = 800 + 400 * (5 - self.diff["ApproachRate"]) / 5
		elif self.diff["ApproachRate"] == 5:
			self.time_preempt = 1200
			self.fade_in = 800
		else:
			self.time_preempt = 1200 - 750 * (self.diff["ApproachRate"] - 5) / 5
			self.fade_in = 800 - 500 * (self.diff["ApproachRate"] - 5) / 5

		self.maxtimewindow = 150 + 50 * (5 - self.diff["OverallDifficulty"]) / 5  # + 0.5
		self.interval = settings.timeframe / settings.fps
		self.CIRCLE = 0
		self.SLIDER = 1
		self.SPINNER = 2

		self.mods = replay.mod_combination
		self.check = Check(beatmap.diff, self.hitobjects, self.mods)
		logging.log(1, "Diff {}".format(self.diff))
		self.scorecounter = 0
		self.combo = 0
		self.maxcombo = 0
		self.mod_multiplier = getmultiplier(self.mods)
		self.results = {300: 0, 100: 0, 50: 0, 0: 0}
		self.clicks = [0, 0, 0, 0]

		self.maxscore = replay.score  # temporary fix to limit the score to this one. Avoid getting higher on leaderboard incorrectly

		self.info = []
		self.starthitobjects = 0
		if not tests:
			self.health_processor = HealthProcessor(beatmap)
		else:
			self.health_processor = HealthDummy(beatmap)
		beatmap.health_processor = self.health_processor
		self.drainrate = self.health_processor.drain_rate
		self.health_value = 1

	def difficulty_multiplier(self):
		return difficulty_multiplier(self.diff)

	def update_score(self, hitresult, objtype, usecombo=True, combo=None):
		# Always update score after updating combo

		if usecombo:
			if combo is None:
				combo = self.combo - 2
			combo = max(0, combo)
			self.scorecounter += int(hitresult + (hitresult * ((combo * self.diff_multiplier * self.mod_multiplier) / 25)))
		else:
			self.scorecounter += int(hitresult)
			if hitresult == 0:
				return
			objtype = []  # no bonus score for new combo
			hitresult = 100 if hitresult < 1000 else 300

		if self.scorecounter >= self.maxscore:
			self.scorecounter = self.maxscore

		self.health_processor.updatehp(hitresult, objtype)

	def getacc(self, acc):
		total = (acc[300] + acc[100] + acc[50] + acc[0]) * 300
		actual = acc[300] * 300 + acc[100] * 100 + acc[50] * 50

		if total == 0:
			return 0

		return actual/total * 100

	def checkcircle(self, note_lock, i, replay, osr_index, sum_newclick):
		update, hitresult, timestamp, idd, x, y, reduceclick, deltat = self.check.checkcircle(i, replay, osr_index,
		                                                                                      sum_newclick, self.combo)
		update = update and (deltat > 0 or abs(deltat) <= self.time_preempt)

		if update:
			state = States.NORMAL
			sum_newclick = max(0, sum_newclick - reduceclick)
			if note_lock:
				state = States.NOTELOCK
				if hitresult != 0 or deltat < 0:  # if it's not because clicked too early
					circle = Circle(state, 0, False, "slider" in self.hitobjects[i]["type"], x, y)
					info = Info(replay[osr_index][3], self.combo, 0, self.scorecounter, self.scorecounter,
					            copy.copy(self.results), copy.copy(self.clicks), None,
					            timestamp, idd, self.health_processor.health_value, self.maxcombo, circle)
					self.info.append(info)
					return note_lock, sum_newclick, i

			if hitresult is None:
				return note_lock, sum_newclick, i

			if hitresult > 0:
				self.combo += 1
				combostatus = 1
				state = States.FADEOUT
			else:
				combostatus = -1
				self.combo = 0

			self.maxcombo = max(self.maxcombo, self.combo)

			if "circle" in self.hitobjects[i]["type"]:
				self.results[hitresult] += 1
				self.update_score(hitresult, self.hitobjects[i]["type"])
			else:
				self.update_score(30 * int(hitresult is not None and hitresult > 0), self.hitobjects[i]["type"], usecombo=False)

			osrtime = min(replay[osr_index][3], self.hitobjects[i]["time"] + self.maxtimewindow + 1)

			if "circle" in self.hitobjects[i]["type"]:
				circle = Circle(state, deltat, False, False, x, y)
				del self.hitobjects[i]
				i -= 1
			else:
				followappear = False
				self.hitobjects[i]["head not done"] = False
				if hitresult != 0:
					self.check.sliders_memory[idd]["score"] += 1
					self.check.sliders_memory[idd]["combo"] += 1

					if replay[osr_index][3] > timestamp:
						delta_time = max(0, (replay[osr_index][3] - self.hitobjects[i]["time"]) % self.hitobjects[i][
							"duration"])
						dist = self.hitobjects[i]["pixel length"] / self.hitobjects[i]["duration"] * delta_time
						pos, t = self.hitobjects[i]["baiser"].at(dist, True, alone=True)  # TODO: what if kick slider too fast and clicked too late
						in_ball = math.sqrt(
							(replay[osr_index][0] - pos[0]) ** 2 + (replay[osr_index][1] - pos[1]) ** 2) <= \
						          self.check.sliders_memory[idd]["dist"]
					else:
						in_ball = True
					if in_ball:
						self.check.sliders_memory[idd]["dist"] = self.check.diff.slidermax_distance
						followappear = True
				elif hitresult == 0:
					self.check.sliders_memory[idd]["combo"] = 0
				circle = Circle(state, deltat, followappear, True, x, y)


			info = Info(osrtime, self.combo, combostatus,
			            self.scorecounter, self.scorecounter,
			            copy.copy(self.results), copy.copy(self.clicks), hitresult, timestamp, idd,
			            self.health_processor.health_value, self.maxcombo, circle)
			self.info.append(info)
		else:
			note_lock = True
		return note_lock, sum_newclick, i

	def checkslider(self, i, replay, osr_index):
		update, hitresult, timestamp, idd, x, y, followappear, hitvalue, combostatus, tickend, updatefollow = self.check.checkslider(
			i, replay, osr_index)

		# slider has notelock and it depends on the hit time window, or if the slider is too short then it would be the duration of the slider
		notelock = replay[osr_index][Replays.TIMES] < min(self.hitobjects[i]["end time"], timestamp + self.maxtimewindow)

		if combostatus > 0:
			self.combo += combostatus
		if combostatus == -1:
			self.combo = 0

		self.maxcombo = max(self.maxcombo, self.combo)

		end = self.check.sliders_memory[idd]["tickend"]
		arrowindex = self.check.sliders_memory[idd]["repeated slider"]

		osrtime = min(replay[osr_index][3], self.hitobjects[i]["end time"] + 1)

		if update:
			self.update_score(hitvalue, self.hitobjects[i]["type"], usecombo=False)
			if hitresult is not None:
				self.results[hitresult] += 1

				if self.hitobjects[i]["head not done"]:
					self.combo = max(0, combostatus)
					circle = Circle(0, 0, followappear, True, x, y)
					info = Info(replay[osr_index][3], 0, -1,
					            self.scorecounter, self.scorecounter,
					            copy.copy(self.results), copy.copy(self.clicks), 0, timestamp, idd,
					            self.health_processor.health_value, self.maxcombo, circle)
					self.info.append(info)

				self.update_score(hitresult, self.hitobjects[i]["type"], combo=self.combo-1)
				del self.hitobjects[i]
				del self.check.sliders_memory[idd]
				i -= 1

		if update or combostatus != 0:
			followstate = str(int(updatefollow)) + str(int(followappear))

			if combostatus > 1:
				for x in range(combostatus, 0, -1):
					slider = Slider(followstate, hitvalue, tickend, x, y, end, arrowindex)
					info = Info(osrtime, self.combo-x, 1,
					            self.scorecounter, self.scorecounter,
					            copy.copy(self.results), copy.copy(self.clicks), hitresult, timestamp, idd,
					            self.health_processor.health_value, self.maxcombo, slider)
					self.info.append(info)
				combostatus = 1

			self.maxcombo = max(self.maxcombo, self.combo)

			slider = Slider(followstate, hitvalue, tickend, x, y, end, arrowindex)

			info = Info(osrtime, self.combo, combostatus,
			            self.scorecounter, self.scorecounter,
			            copy.copy(self.results), copy.copy(self.clicks), hitresult, timestamp, idd,
			            self.health_processor.health_value, self.maxcombo, slider)
			self.info.append(info)

		return notelock, i

	def checkspinner(self, i, replay, osr_index):
		update, cur_rot, progress, hitresult, bonusscore, hitvalue = self.check.checkspinner(i, replay, osr_index)
		combostatus = 0
		idd = self.hitobjects[i]["id"]
		timestamp = self.hitobjects[i]["time"]
		self.update_score(hitvalue, self.hitobjects[i]["type"], usecombo=False)
		if update:
			osrtime = min(replay[osr_index][3], self.hitobjects[i]["end time"] + 1)
			if hitresult is not None:

				self.results[hitresult] += 1
				if hitresult > 0:
					self.combo += 1
					combostatus = 1
					self.update_score(hitresult, self.hitobjects[i]["type"])
				else:
					self.combo = 0
					combostatus = -1
				osrtime = self.hitobjects[i]["end time"] + 1
				del self.hitobjects[i]
				i -= 1

			self.maxcombo = max(self.maxcombo, self.combo)

			if bonusscore >= 1:
				self.update_score(1000, self.hitobjects[i]["type"], usecombo=False)

			spinner = Spinner(cur_rot, progress, bonusscore, hitvalue)


			info = Info(osrtime, self.combo, combostatus,
			            self.scorecounter, self.scorecounter,
			            copy.copy(self.results), copy.copy(self.clicks), hitresult, timestamp, idd,
			            self.health_processor.health_value, self.maxcombo, spinner)
			self.info.append(info)
		return i

	def checkcursor(self, replay, new_click, osr_index, in_break):
		note_lock = False
		sum_newclick = sum(new_click)
		self.clicks[0] += new_click[0]
		self.clicks[1] += new_click[1]
		self.clicks[2] += new_click[2]
		self.clicks[3] += new_click[3]

		i = 0
		inrange = True

		self.health_processor.drainhp(replay[osr_index][3], replay[osr_index - 1][3], in_break)

		while inrange and i < len(self.hitobjects) - 1:
			if "circle" in self.hitobjects[i]["type"]:
				note_lock, sum_newclick, i = self.checkcircle(note_lock, i, replay, osr_index, sum_newclick)

			elif "slider" in self.hitobjects[i]["type"]:
				if self.hitobjects[i]["head not done"]:
					note_lock, sum_newclick, i = self.checkcircle(note_lock, i, replay, osr_index, sum_newclick)
				note_lock, i = self.checkslider(i, replay, osr_index)

			elif "spinner" in self.hitobjects[i]["type"]:
				i = self.checkspinner(i, replay, osr_index)
			i += 1

			if i >= len(self.hitobjects) - 1:
				break

			self.maxcombo = max(self.maxcombo, self.combo)
			mintime = self.hitobjects[i]["time"] - self.fade_in <= replay[osr_index][3]
			maxtime = replay[osr_index][3] <= self.hitobjects[i]["end time"] + self.maxtimewindow + self.interval * 2
			inrange = mintime and maxtime
