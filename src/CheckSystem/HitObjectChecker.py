from CheckSystem.Judgement import Check
from collections import namedtuple
import copy


Info = namedtuple("Info", "time combo combostatus showscore score accuracy clicks hitresult timestamp more")
Circle = namedtuple("Circle", "state deltat followstate sliderhead x y")
Slider = namedtuple("Slider", "followstate hitvalue tickend x y")
Spinner = namedtuple("Spinner", "rotate progress bonusscore hitvalue")


class HitObjectChecker:
	def __init__(self, beatmap, settings, mod=1):
		self.diff = beatmap.diff
		self.hitobjects = copy.deepcopy(beatmap.hitobjects) # TODO: put slider image into another list
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

		self.maxtimewindow = 150 + 50 * (5 - self.diff["OverallDifficulty"]) / 5  # - 0.5
		self.interval = settings.timeframe / settings.fps
		self.CIRCLE = 0
		self.SLIDER = 1
		self.SPINNER = 2

		self.check = Check(beatmap.diff, self.hitobjects)

		self.scorecounter = 0
		self.combo = 0
		self.mod = mod
		self.results = {300: 0, 100: 0, 50: 0, 0: 0}
		self.clicks = [0, 0, 0, 0]

		self.info = []
		self.starthitobjects = 0

	def difficulty_multiplier(self):
		points = self.diff["BaseOverallDifficulty"] + self.diff["BaseHPDrainRate"] + self.diff["BaseCircleSize"]
		if points in range(0, 6):
			return 2
		if points in range(6, 13):
			return 3
		if points in range(13, 18):
			return 4
		if points in range(18, 25):
			return 5
		return 6

	def update_score(self, hitresult):
		combo = max(0, self.combo - 1)
		self.scorecounter += int(hitresult + (hitresult * ((combo * self.diff_multiplier * self.mod) / 25)))

	def checkcircle(self, note_lock, i, replay, osr_index, sum_newclick):
		update, hitresult, timestamp, x, y, reduceclick, deltat = self.check.checkcircle(i, replay, osr_index, sum_newclick)
		if update:
			state = 0
			sum_newclick = max(0, sum_newclick - reduceclick)
			if note_lock:
				state = 1
				if hitresult != 0 or deltat < 0:  # if it's not because clicked too early
					circle = Circle(state, 0, False, "slider" in self.hitobjects[i]["type"], x, y)
					info = Info(replay[osr_index][3], -1, 0, self.scorecounter, -1, -1, self.clicks, None,
					            timestamp, circle)
					self.info.append(info)
					return note_lock, sum_newclick, i

			followappear = False
			if hitresult > 0:
				self.combo += 1
				combostatus = 1
				state = 2
				followappear = True
			else:
				combostatus = -1
				self.combo = 0

			if "circle" in self.hitobjects[i]["type"]:
				self.results[hitresult] += 1

			# self.scorecounter.update_score(max(0, self.combo - 1), hitresult) # TODO: what if circle is sliderhead and hitresult is 100
			self.update_score(hitresult)

			circle = Circle(state, deltat, followappear, "slider" in self.hitobjects[i]["type"], x, y)
			info = Info(replay[osr_index][3], self.combo, combostatus,
			            self.scorecounter, self.scorecounter,
			            copy.copy(self.results), copy.copy(self.clicks), hitresult, timestamp, circle)
			self.info.append(info)

			if "circle" in self.hitobjects[i]["type"]:
				del self.hitobjects[i]
				i -= 1
			else:
				self.hitobjects[i]["head not done"] = False
				if hitresult != 0:
					self.check.sliders_memory[timestamp]["score"] += 1
					if replay[osr_index][3] <= timestamp:
						self.check.sliders_memory[timestamp]["dist"] = self.check.diff.slidermax_distance
		else:
			note_lock = True
		return note_lock, sum_newclick, i

	def checkslider(self, i, replay, osr_index):
		update, hitresult, timestamp, x, y, followappear, hitvalue, combostatus, tickend = self.check.checkslider(i, replay, osr_index)
		self.scorecounter += hitvalue
		if combostatus == 1:
			self.combo += 1
		if combostatus == -1:
			self.combo = 0

		if update:
			if hitresult is not None:
				self.results[hitresult] += 1

				if tickend:
					self.update_score(hitresult)

				del self.hitobjects[i]
				del self.check.sliders_memory[timestamp]
				i -= 1

		if update or combostatus != 0:
			followstate = str(int(update)) + str(int(followappear))
			slider = Slider(followstate, hitvalue, tickend, x, y)
			info = Info(replay[osr_index][3], self.combo, combostatus,
			            self.scorecounter, self.scorecounter,
			            copy.copy(self.results), copy.copy(self.clicks), hitresult, timestamp, slider)
			self.info.append(info)

		return i

	def checkspinner(self, i, replay, osr_index):
		update, cur_rot, progress, hitresult, bonusscore, hitvalue = self.check.checkspinner(i, replay[osr_index])
		combostatus = 0
		timestamp = self.hitobjects[i]["id"]
		self.scorecounter += hitvalue
		if update:
			if hitresult is not None:
				self.results[hitresult] += 1

				if hitresult > 0:
					self.combo += 1
					combostatus = 1
				else:
					self.combo = 0
					combostatus = -1
				del self.hitobjects[i]
				i -= 1

			if bonusscore >= 1:
				self.scorecounter += bonusscore * 1000  # TODO: fix score

			spinner = Spinner(cur_rot, progress, bonusscore, hitvalue)
			info = Info(replay[osr_index][3], self.combo, combostatus,
			            self.scorecounter, self.scorecounter,
			            copy.copy(self.results), copy.copy(self.clicks), hitresult, timestamp, spinner)
			self.info.append(info)
		return i

	def checkcursor(self, replay, new_click, osr_index):
		note_lock = False
		sum_newclick = sum(new_click)
		self.clicks[0] += new_click[0]
		self.clicks[1] += new_click[1]
		self.clicks[2] += new_click[2]
		self.clicks[3] += new_click[3]

		i = 0
		inrange = True
		# self.scorecounter.add_to_frame(None, replay[osr_index][3])

		while inrange and i < len(self.hitobjects)-1:
			if "circle" in self.hitobjects[i]["type"]:
				note_lock, sum_newclick, i = self.checkcircle(note_lock, i, replay, osr_index, sum_newclick)

			elif "slider" in self.hitobjects[i]["type"]:
				if self.hitobjects[i]["head not done"]:
					note_lock, sum_newclick, i = self.checkcircle(note_lock, i, replay, osr_index, sum_newclick)
				i = self.checkslider(i, replay, osr_index)

			elif "spinner" in self.hitobjects[i]["type"]:
				i = self.checkspinner(i, replay, osr_index)
			i += 1

			if i >= len(self.hitobjects)-1:
				break

			mintime = self.hitobjects[i]["time"] - self.fade_in <= replay[osr_index][3]
			maxtime = replay[osr_index][3] <= self.hitobjects[i]["end time"] + self.maxtimewindow + self.interval * 2
			inrange = mintime and maxtime
