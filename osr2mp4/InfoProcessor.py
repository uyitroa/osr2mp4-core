import atexit

from oppai import *
from osr2mp4.EEnum.EState import States
from osr2mp4.Utils.cubic_interp1d import cubic_interp1d
from numpy import arange, maximum
import matplotlib.pyplot as plt

class Updater:
	counter = 0

	def __init__(self, resultinfo, component, settings, mods, osufile):
		self.resultinfo = resultinfo
		self.component = component
		self.info_index = 0
		self.info = self.resultinfo[0]
		self.idd = self.counter
		self.counter += 1
		self.settings = settings
		if settings.settings["Enable PP counter"] or settings.settings["Enable Strain Graph"]:
			self.ez = ezpp_new()
			ezpp_set_autocalc(self.ez, 1)
			ezpp_dup(self.ez, osufile)
			self.ezpp_setmods(mods)
			atexit.register(self.freeezpp)
			
			if(settings.settings["Enable Strain Graph"]):
				# get time info
				nobjects = ezpp_nobjects(self.ez)
				total_time = int(ezpp_time_at(self.ez, nobjects-1))
				# auto calculate time window
				settings.strainsettings["TimeWindowInSeconds"] = total_time / float(settings.strainsettings["GraphDensity"])
				# calculate strain
				self.strains = self.ezpp_calculate_strain(nobjects, total_time, settings.strainsettings["TimeWindowInSeconds"])
				# smooth strain
				strain_x, smoothed_strains = self.smooth_strain([s[2] for s in self.strains], settings.strainsettings["Smoothing"]) # use total strain for now
				# create a plot and save it
				fig = plt.figure(figsize=tuple(settings.strainsettings["AspectRatio"]), dpi=60)
				plt.axis('off')
				plt.margins(0,0)
				graph_color = tuple(t/255.0 for t in settings.strainsettings["Rgb"]) + (1.0,)
				plt.fill_between(strain_x, smoothed_strains, color=graph_color)
				plt.savefig(settings.temp + 'strain.png', bbox_inches='tight', transparent="True", pad_inches=0)

	def ezpp_calculate_strain(self, nobjects, total_time, time_interval_in_ms):
		t = []
		for x in arange(0, total_time+time_interval_in_ms, time_interval_in_ms):
			aim_strain = 0
			speed_strain = 0
			total = 0
			for o in range(nobjects):
				time = int(ezpp_time_at(self.ez, o))
				if((time >= x) and (time < x + time_interval_in_ms)):
					aim_strain += ezpp_strain_at(self.ez, o, 0)
					speed_strain += ezpp_strain_at(self.ez, o, 1)
					total += aim_strain + speed_strain
			t.append([aim_strain, speed_strain, total])
		return t

	def smooth_strain(self, series, smooth_factor):
		old_t = list(range(0,len(series)))
		new_t = arange(0, len(series)-1, 1.0/smooth_factor)
		return (new_t, maximum(0,cubic_interp1d(new_t, old_t, series)))

	def ezpp_setmods(self, playermods):
		playermodezpp = MODS_NOMOD
		for playermod in playermods:
			playermodezpp |= playermod
		ezpp_set_mods(self.ez, playermodezpp)

	def freeezpp(self):
		ezpp_free(self.ez)

	def process_pp(self):
		if not self.settings.settings["Enable PP counter"]:
			return
		ezpp_set_accuracy(self.ez, self.info.accuracy[100], self.info.accuracy[50])
		ezpp_set_nmiss(self.ez, self.info.accuracy[0])
		ezpp_set_combo(self.ez, self.info.maxcombo)
		ezpp_set_end(self.ez, self.info.id+1)
		curpp = ezpp_pp(self.ez)
		self.component.ppcounter.update(curpp)

	def process_combo(self):
		if self.info.combostatus == 1:
			self.component.combocounter.add_combo(combo=self.info.combo)
		elif self.info.combostatus == -1:
			self.component.combocounter.breakcombo()

		self.component.flashlight.set_combo(self.info.combo)

	def process_acc(self):
		objtype = type(self.info.more).__name__
		if objtype == "Circle":
			idd = str(self.info.id) + "c"
			if idd not in self.component.hitobjmanager.circle_manager.circles:
				return

			x, y = self.info.more.x, self.info.more.y
			if self.info.more.state == States.NOTELOCK and self.info.more.sliderhead is False:
				self.component.hitobjmanager.notelock_circle(idd)
			elif self.info.more.state == States.FADEOUT:
				self.component.hitobjmanager.fadeout_circle(idd)
				self.component.urbar.add_bar(self.info.more.deltat, self.info.hitresult)
				if self.info.more.sliderhead:
					self.component.hitobjmanager.sliderchangestate(self.info.more.followstate, str(self.info.id) + "s")
				else:
					self.component.flashlight.set_sliding(False)
			if self.info.hitresult == 0:
				self.component.hitobjmanager.delete_circle(idd)

		elif objtype == "Slider":
			idd = str(self.info.id) + "s"
			if idd not in self.component.hitobjmanager.slider_manager.sliders:
				return

			x, y = self.info.more.x, self.info.more.y
			followbit = self.info.more.followstate
			if int(followbit[0]):
				self.component.hitobjmanager.sliderchangestate(int(followbit[1]), idd)
				self.component.flashlight.set_sliding(int(followbit[1]))

			if self.info.more.hitvalue == 10:
				self.component.hitobjmanager.slidertouchtick(idd)

			if self.info.more.hitvalue != 0:
				self.component.scorebar.to_hp(self.info.hp)

			self.component.scorecounter.bonus_score(self.info.more.hitvalue)

		else:
			idd = str(self.info.id) + "o"
			if idd not in self.component.hitobjmanager.spinner_manager.spinners:
				return

			y, x = 384 * 0.5, 512 * 0.5
			self.component.spinner.update_spinner(idd, self.info.more.rotate, self.info.more.progress, self.info.more.rpm)

			self.component.scorecounter.bonus_score(self.info.more.hitvalue)
			if self.info.more.hitvalue != 0:
				self.component.scorebar.to_hp(self.info.hp)

			if self.info.more.bonusscore >= 1:
				if int(self.component.spinbonus.spinbonuses[0])/1000 != self.info.more.bonusscore:
					self.component.scorecounter.bonus_score(1000)
					self.component.scorebar.to_hp(self.info.hp)
				self.component.spinbonus.set_bonusscore(self.info.more.bonusscore)

		if self.info.hitresult is not None:
			self.component.scorebar.to_hp(self.info.hp)
			if not (objtype == "Circle" and self.info.more.sliderhead):
				self.component.hitresult.add_result(self.info.hitresult, x, y)
				self.component.accuracy.update_acc(self.info.hitresult)
			if objtype != "Slider" or self.info.more.hitend:
				self.component.scorecounter.update_score(self.info.score)

		self.component.scoreboard.setscore(self.info.score, self.info.maxcombo)
		self.component.hitresultcounter.update(self.info.accuracy)

	def update(self, cur_time):
		if self.info_index >= len(self.resultinfo) or self.resultinfo[self.info_index].time > cur_time:
			return
		while self.info_index < len(self.resultinfo) and self.resultinfo[self.info_index].time < cur_time:
			self.info = self.resultinfo[self.info_index]
			self.process_combo()
			self.process_acc()
			self.info_index += 1
		self.process_pp()
