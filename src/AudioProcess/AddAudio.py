from AudioProcess.Hitsound import Hitsound
from AudioProcess.Utils import overlay


class HitsoundManager:
	def __init__(self, beatmap):
		self.hitobjects = beatmap.hitobjects
		self.breakperiods = beatmap.breakperiods
		self.spincooldown = 0
		self.prevspin = None
		self.prevbonusscore = None
		self.breakperiod_i = 0
		self.sectionadded = False

	def addsectionsound(self, my_info, index, song):
		if self.breakperiods[self.breakperiod_i]["End"] < my_info[index].time:
			self.breakperiod_i += 1
			self.sectionadded = False
		breakperiod = self.breakperiods[self.breakperiod_i]

		if self.sectionadded or self.breakperiod_i >= len(self.breakperiods)-1:
			return

		self.sectionadded = True
		half = breakperiod["Start"] + (breakperiod["End"] - breakperiod["Start"]) / 2
		print(half)
		if breakperiod["End"] - breakperiod["Start"] > 2000:
			if my_info[index].hp < 0.5:
				sound = Hitsound.sectionfail
			else:
				sound = Hitsound.sectionpass
			overlay(half, song, sound)
			self.sectionadded = True

	def addcombobreak(self, my_info, index, song):
		previndex = max(0, index - 1)
		if my_info[previndex].combo > 20 and my_info[index].combostatus == -1:
			overlay(my_info[index].time, song, Hitsound.miss)

	def addhitsound(self, my_info, index, song):
		if type(my_info[index].more).__name__ == "Circle":
			if my_info[index].hitresult is not None and my_info[index].hitresult > 0:
				overlay(my_info[index].time, song, Hitsound.normalhitnormal)

	def addslidersound(self, my_info, index, song):
		if type(my_info[index].more).__name__ == "Slider":
			objectindex = my_info[index].id

			if my_info[index].more.hitvalue == 10:
				overlay(my_info[index].time, song, Hitsound.normalslidertick)

			if my_info[index].more.hitvalue >= 30 and not my_info[index].more.end:  # in case sliderend and sliderarrow has same time because fast slider so need >= 30
				overlay(my_info[index].time, song, Hitsound.normalhitnormal)

			if my_info[index].hitresult is not None and my_info[index].hitresult > 0:
				endtime = self.hitobjects[objectindex]["end time"]
				overlay(endtime, song, Hitsound.normalhitnormal)

	def addspinnerhitsound(self, my_info, index, song):
		if type(my_info[index].more).__name__ == "Spinner":
			if my_info[index].time > self.spincooldown:
				if self.prevspin is None or self.prevspin.progress != my_info[index].more.progress:
					spinsound = int(min(1, my_info[index].more.progress) * (len(Hitsound.spinnerspin)-1))
					overlay(my_info[index].time, song, Hitsound.spinnerspin[spinsound])
					self.spincooldown = my_info[index].time + len(Hitsound.spinnerspin[spinsound].audio)/Hitsound.spinnerspin[spinsound].rate * 1000
			self.prevspin = my_info[index].more

			if self.prevbonusscore != my_info[index].more.bonusscore and my_info[index].more.bonusscore > 0:
				overlay(my_info[index].time, song, Hitsound.spinnerbonus)
				self.prevbonusscore = my_info[index].more.bonusscore
