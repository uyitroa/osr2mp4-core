import logging

from recordclass import recordclass

from osr2mp4.osrparse.enums import Mod
from osr2mp4.EEnum.EReplay import Replays
from osr2mp4.CheckSystem.HitObjects.HitObject import HitObject


Transformation = recordclass("Transformation", "startvector endvector time1 time2")


class Slider(HitObject):
	def __init__(self, hitobject, combo):
		self.osu_d = hitobject
		self.sliderballtransformations = []
		self.slider_score_timingpoints = []
		self.curscore = 0
		self.maxscore = 1
		self.issliding = False
		self.combo = combo
		self.hitend = False
		self.n_arrow = 1
		self.prev_issliding = False

		self.ticks_hit = 0
		self.ticks_miss = 0

		self.starttime, self.duration = int(self.osu_d["time"]), self.osu_d["duration"]
		self.endtime = self.starttime + self.duration * self.osu_d["repeated"]

		self.getsliderballtransformations()

	def getsliderballtransformations(self):
		cum_length = self.osu_d["slider_c"].cum_length
		currenttime = self.starttime
		scoringdistance = 0
		scoringlengthtotal = 0
		tickdistance = self.osu_d["tickdistance"]
		mintickdistancefromend = 0.01 * self.osu_d["velocity"]

		for i in range(self.osu_d["repeated"]):
			reverse = i % 2 == 1
			start = len(cum_length)-1 if reverse else 0
			end = -1 if reverse else len(cum_length)
			direction = -1 if reverse else 1
			j = start

			skiptick = False
			distancetoend = cum_length[-1]

			while j != end:
				distance = cum_length[j] - (0 if j == 0 else cum_length[j-1])
				duration = 1000 * distance / self.osu_d["velocity"]

				if reverse:
					p2 = self.osu_d["slider_c"].pos[j]
					p1 = self.osu_d["slider_c"].pos[j+1]
				else:
					p1 = self.osu_d["slider_c"].pos[j]
					p2 = self.osu_d["slider_c"].pos[j+1]

				self.sliderballtransformations.append(Transformation(p1, p2, int(currenttime), int(currenttime + duration)))

				currenttime += duration
				j += direction
				scoringdistance += distance

				while scoringdistance >= tickdistance and not skiptick:
					scoringlengthtotal += tickdistance
					scoringdistance -= tickdistance
					distancetoend -= tickdistance
					skiptick = distancetoend <= mintickdistancefromend
					if skiptick:
						break
					scoretime = self.timeatlength(scoringlengthtotal)
					self.slider_score_timingpoints.append(scoretime)

			scoringlengthtotal += scoringdistance
			self.slider_score_timingpoints.append(self.timeatlength(scoringlengthtotal))

			if skiptick:
				scoringdistance = 0
			else:
				scoringlengthtotal -= tickdistance - scoringdistance
				scoringdistance = tickdistance - scoringdistance

		if len(self.slider_score_timingpoints) > 0:
			self.slider_score_timingpoints[-1] = max(self.starttime + (self.endtime - self.starttime)//2, self.slider_score_timingpoints[-1] - 36)

	def timeatlength(self, length):
		return int(self.starttime + (length/self.osu_d["velocity"]) * 1000)

	def find(self, curtime):
		for i in range(len(self.sliderballtransformations)):
			if self.sliderballtransformations[i].time1 <= curtime <= self.sliderballtransformations[i].time2:
				return i
		return len(self.sliderballtransformations)-1

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
		return cursor_distance < radius * radius

	def check(self, replay, osrindex):
		osr = replay[osrindex]
		curtime = osr[Replays.TIMES]

		hitvalue = combostatus = 0
		updatefollow = False

		if self.endtime >= osr[3] >= self.starttime:
			hitvalue, combostatus = self.check_cursor_incurve(replay, osrindex)
			updatefollow = self.prev_issliding != self.issliding

		elif self.starttime - self.diff.scorewindow[2] < curtime <= self.starttime:
			pos = self.osu_d["slider_c"].at(0)
			self.issliding = self.cursor_inslider(osr, pos) and osr[Replays.KEYS_PRESSED] != 0

		if osr[3] > self.endtime:
			hitresult = self.gethitresult()
			return True, hitresult, self.starttime, self.osu_d["id"], self.osu_d["end x"], self.osu_d["end y"], False, hitvalue, combostatus, self.hitend, True

		if updatefollow or hitvalue != 0:
			self.prev_issliding = self.issliding
			return True, None, self.starttime, self.osu_d["id"], 0, 0, self.issliding, hitvalue, combostatus, 0, updatefollow

		return False, None, self.starttime, self.osu_d["id"], self.osu_d["end x"], self.osu_d["end y"], self.issliding, hitvalue, combostatus, 0, False

	def check_cursor_incurve(self, replay, osrindex):

		osr = replay[osrindex]
		curtime = osr[Replays.TIMES]

		allowable = False
		mousedown = osr[Replays.KEYS_PRESSED] != 0 or Mod.Relax in self.mods

		if mousedown:
			index = self.find(curtime)
			sb = self.sliderballtransformations[index]
			if sb.time1 == sb.time2:
				pos = [sb.endvector[0], sb.endvector[1]]
			else:
				x = sb.startvector[0] + (sb.endvector[0] - sb.startvector[0]) * (1 - (sb.time2 - curtime)/(sb.time2 - sb.time1))
				y = sb.startvector[1] + (sb.endvector[1] - sb.startvector[1]) * (1 - (sb.time2 - curtime)/(sb.time2 - sb.time1))
				pos = [x, y]
			allowable = self.cursor_inslider(osr, pos)

		pointcount = 0
		while pointcount < len(self.slider_score_timingpoints) and self.slider_score_timingpoints[pointcount] <= curtime:
			pointcount += 1

		combostatus = 0
		hitvalue = 0

		if self.ticks_miss + self.ticks_hit < pointcount:
			self.maxscore += 1
			if allowable:
				self.ticks_hit += 1
				self.curscore += 1
				combostatus = 1

				if pointcount == len(self.slider_score_timingpoints):
					self.hitend = True
					hitvalue = 30

				elif pointcount % (len(self.slider_score_timingpoints)/self.osu_d["repeated"]) == 0:
					self.n_arrow += 1
					hitvalue = 30
				else:
					hitvalue = 10

			else:
				self.ticks_miss += 1
				if pointcount != len(self.slider_score_timingpoints):
					combostatus = -1

				if pointcount % (len(self.slider_score_timingpoints) / self.osu_d["repeated"]) == 0:
					self.n_arrow += 1

		self.issliding = allowable

		return hitvalue, combostatus
