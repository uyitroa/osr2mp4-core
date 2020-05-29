from .Hitsound import Hitsound
from .Utils import overlay, getfilename, overlays
from ..EEnum.EAudio import Sound


class HitsoundManager:
	def __init__(self, beatmap):
		self.hitobjects = beatmap.hitobjects
		self.breakperiods = beatmap.breakperiods
		self.timingpoint = beatmap.timing_point
		self.timingpoint_index = 0
		self.spincooldown = 0
		self.prevspin = None
		self.prevbonusscore = None
		self.breakperiod_i = 0
		self.sectionadded = False

		self.hitsoundset = {"0": "normal", "1": "whistle", "2": "finish", "3": "clap"}
		self.sliderset = {"0": "slide", "1": "whilstle"}
		self.sampleset = {"0": "normal", "1": "normal", "2": "soft", "3": "drum"}

	def getvolume(self, samplevolume):
		if float(samplevolume) == 0:
			return self.timingpoint[self.timingpoint_index]["Volume"]/100
		return float(samplevolume)/100

	def updatetimingpoint(self, my_info, index, song):
		# use next off_set or not

		cur_time = my_info[index].time
		if type(my_info[index].more).__name__ == "Circle":
			cur_time = my_info[index].timestamp
		if type(my_info[index].more).__name__ == "Slider":
			slidertime = my_info[index].timestamp + self.hitobjects[my_info[index].id]["duration"] * (my_info[index].more.arrowindex-1)
			cur_time = max(cur_time, slidertime)

		while cur_time >= self.timingpoint[self.timingpoint_index + 1]["Offset"] - 1:
			self.timingpoint_index += 1

	def addsectionsound(self, my_info, index, song):
		if self.breakperiods[self.breakperiod_i]["End"] < my_info[index].time:
			self.breakperiod_i += 1
			self.sectionadded = False
		breakperiod = self.breakperiods[self.breakperiod_i]

		if self.sectionadded or self.breakperiod_i >= len(self.breakperiods)-1:
			return

		self.sectionadded = True
		half = breakperiod["Start"] + (breakperiod["End"] - breakperiod["Start"]) / 2
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
				objectindex = my_info[index].id
				my_dict = self.hitobjects[objectindex]

				tt = "soundcircle"
				hitvolume = my_dict["hitSample"][Sound.volume]
				if my_info[index].more.sliderhead:
					tt = "soundhead"
					hitvolume = "0"

				# overlay(my_info[index].time, song, Hitsound.hitsounds[my_dict[tt][0]], volume=self.getvolume(hitvolume))
				# for f in my_dict[tt][1:]:
				# 	overlay(my_info[index].time, song, Hitsound.hitsounds[f], volume=self.getvolume(hitvolume) * 0.5)

				overlays(my_info[index].time, song, my_dict[tt], volume=self.getvolume(hitvolume))

	def addslidersound(self, my_info, index, song):
		if type(my_info[index].more).__name__ == "Slider":
			objectindex = my_info[index].id
			my_dict = self.hitobjects[objectindex]

			if my_info[index].more.hitvalue == 10:
				overlays(my_info[index].time, song, my_dict["soundtick"], volume=self.getvolume(0))

			if my_info[index].more.hitvalue >= 30 and not my_info[index].more.end:  # in case sliderend and sliderarrow has same time because fast slider so need >= 30
				overlays(my_info[index].time, song, my_dict["soundarrow{}".format(my_info[index].more.arrowindex-1)], volume=self.getvolume(0))

			if my_info[index].hitresult is not None and my_info[index].hitresult > 0:
				endtime = self.hitobjects[objectindex]["end time"]
				overlays(endtime, song, my_dict["soundend"], volume=self.getvolume(0))

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
