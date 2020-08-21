import logging

from ...osrparse.enums import Mod
from ...EEnum.EReplay import Replays
from .HitObject import HitObject


class Slider(HitObject):
	def __init__(self, hitobject, combo):
		self.osu_d = hitobject
		self.slider_score_dist = []
		self.slider_score_timingpoints = []
		self.curscore = 0
		self.maxscore = 1
		self.issliding = False
		self.combo = combo
		self.hitend = False
		self.n_arrow = 1

		self.ticks_hit = 0
		self.ticks_miss = 0

		self.starttime, self.duration = int(self.osu_d["time"]), int(self.osu_d["duration"])
		self.endtime = self.starttime + self.duration * self.osu_d["repeated"]

		velocity = self.osu_d["pixel length"]/self.duration
		time_interval = 0
		if len(self.osu_d["ticks dist"]) > 0:
			tick_distance = self.osu_d["ticks dist"][0]
			time_interval = tick_distance/velocity

		count = 0
		for i in range(self.osu_d["repeated"]):
			if i > 0:
				arrowtime = self.starttime + self.duration * i
				self.slider_score_timingpoints.append(int(arrowtime))

			self.slider_score_timingpoints.extend([self.starttime + time_interval * (count + x + 1) for x in range(len(self.osu_d["ticks dist"]))])
			count += len(self.osu_d["ticks dist"])

		sliderendtime = max(self.starttime + (self.endtime - self.starttime)/2, self.endtime - 36)
		self.slider_score_timingpoints.append(int(sliderendtime))

	def gethitresult(self):
		if self.curscore == 0:
			hitresult = 0
		elif self.curscore < self.maxscore / 2:
			hitresult = 50
		elif self.curscore < self.maxscore:
			hitresult = 100
		elif self.curscore == self.maxscore:
			hitresult = 300
		else:
			hitresult = 300
			logging.warning("what {} {}".format(self.curscore, self.maxscore))

		return hitresult

	def getsliderelapsedtime(self, curtime):
		slidertime = curtime - self.starttime
		reverse = int(slidertime/self.duration) % 2 == 1
		timeatlength = slidertime % self.duration
		timeatlength = self.duration - timeatlength if reverse else timeatlength
		return timeatlength

	def cursor_inslider(self, osr, pos):
		radius = self.diff.slidermax_distance if self.issliding else self.diff.max_distance
		cursor_distance = (round(osr[Replays.CURSOR_X], 2) - pos[0]) ** 2 + (round(osr[Replays.CURSOR_Y], 2) - pos[1]) ** 2
		if self.starttime == 307397:
			print(cursor_distance, self.diff.max_distance**2, self.diff.slidermax_distance**2)
		return cursor_distance < radius * radius

	def check(self, replay, osrindex):
		osr = replay[osrindex]

		hitvalue = combostatus = 0
		prev_state = self.issliding

		if self.endtime >= osr[3] >= self.starttime:
			hitvalue, combostatus = self.check_cursor_incurve(replay, osrindex)

		elif self.starttime - self.diff.score[2] < osr[Replays.TIMES] <= self.starttime:
			pos = self.osu_d["slider_c"].at(0)
			if self.starttime == 307397:
				print(osr, pos)
			self.issliding = self.cursor_inslider(osr, pos) and osr[Replays.KEYS_PRESSED] != 0

		updatefollow = prev_state != self.issliding

		if osr[3] > self.endtime:
			hitresult = self.gethitresult()
			return True, hitresult, self.starttime, self.osu_d["id"], self.osu_d["end x"], self.osu_d["end y"], False, hitvalue, combostatus, self.hitend, True

		if updatefollow or hitvalue != 0:
			return True, None, self.starttime, self.osu_d["id"], 0, 0, self.issliding, hitvalue, combostatus, 0, updatefollow

		return False, None, self.starttime, self.osu_d["id"], self.osu_d["end x"], self.osu_d["end y"], self.issliding, hitvalue, combostatus, 0, False

	def check_cursor_incurve(self, replay, osrindex):

		osr = replay[osrindex]
		allowable = False
		mousedown = osr[Replays.KEYS_PRESSED] != 0 or Mod.Relax in self.mods

		slidertime = self.getsliderelapsedtime(osr[Replays.TIMES])
		pos = [0, 0]
		if mousedown:
			distance = slidertime/self.duration * self.osu_d["pixel length"]
			pos = self.osu_d["slider_c"].at(distance)
			if self.starttime == 307397:
				print(slidertime, distance, pos, self.osu_d["slider_c"].slider_type)
			allowable = self.cursor_inslider(osr, pos)

		pointcount = 0
		while pointcount < len(self.slider_score_timingpoints) and self.slider_score_timingpoints[pointcount] <= osr[Replays.TIMES]:
			pointcount += 1

		combostatus = 0
		hitvalue = 0

		if self.ticks_miss + self.ticks_hit < pointcount:
			self.maxscore += 1
			if allowable:
				self.ticks_hit += 1
				combostatus = 1

				if pointcount == len(self.slider_score_timingpoints):
					self.hitend = True
					hitvalue = 30
					self.curscore += 1

				elif pointcount % (len(self.slider_score_timingpoints)/self.osu_d["repeated"]) == 0:
					self.n_arrow += 1
					self.curscore += 1
					hitvalue = 30
				else:
					hitvalue = 10
					self.curscore += 1

			else:
				self.ticks_miss += 1
				if pointcount != len(self.slider_score_timingpoints):
					combostatus = -1

				if pointcount % (len(self.slider_score_timingpoints) / self.osu_d["repeated"]) == 0:
					self.n_arrow += 1

		if self.starttime == 307397:
			print(self.osu_d["repeated"])
			print(mousedown, allowable, self.ticks_miss, self.ticks_hit, pointcount, self.slider_score_timingpoints, osr, self.endtime, pos, self.duration, "\n")

		self.issliding = allowable

		return hitvalue, combostatus
