from .EEnum.EState import States


class Updater:
	counter = 0

	def __init__(self, resultinfo, component):
		self.resultinfo = resultinfo
		self.component = component
		self.info_index = 0
		self.idd = self.counter
		self.counter += 1

	def process_combo(self):
		if self.info.combostatus == 1:
			self.component.combocounter.add_combo(combo=self.info.combo)
		elif self.info.combostatus == -1:
			self.component.combocounter.breakcombo()

	def process_acc(self):
		objtype = type(self.info.more).__name__
		if objtype == "Circle":
			idd = str(self.info.id) + "c"
			x, y = self.info.more.x, self.info.more.y
			if self.info.more.state == States.NOTELOCK and self.info.more.sliderhead is False:
				self.component.hitobjmanager.notelock_circle(idd)
			elif self.info.more.state == States.FADEOUT:
				self.component.hitobjmanager.fadeout_circle(idd)
				self.component.urbar.add_bar(self.info.more.deltat, self.info.hitresult)
				if self.info.more.sliderhead:
					self.component.hitobjmanager.sliderchangestate(self.info.more.followstate, str(self.info.id) + "s")

		elif objtype == "Slider":
			idd = str(self.info.id) + "s"
			x, y = self.info.more.x, self.info.more.y
			followbit = self.info.more.followstate
			if int(followbit[0]):
				self.component.hitobjmanager.sliderchangestate(int(followbit[1]), idd)

			if self.info.more.hitvalue == 10:
				self.component.hitobjmanager.slidertouchtick(idd)

			if self.info.more.hitvalue != 0:
				self.component.scorebar.to_hp(self.info.hp)

			self.component.scorecounter.bonus_score(self.info.more.hitvalue)

		else:
			idd = str(self.info.id) + "o"
			y, x = 384 * 0.5, 512 * 0.5
			self.component.spinner.update_spinner(idd, self.info.more.rotate, self.info.more.progress)

			self.component.scorecounter.bonus_score(self.info.more.hitvalue)
			if self.info.more.bonusscore >= 1:
				self.component.spinbonus.set_bonusscore(self.info.more.bonusscore)

		if self.info.hitresult is not None:
			self.component.scorebar.to_hp(self.info.hp)
			if not (objtype == "Circle" and self.info.more.sliderhead):
				self.component.hitresult.add_result(self.info.hitresult, x, y)
				self.component.accuracy.update_acc(self.info.hitresult)
			if objtype != "Slider" or self.info.more.tickend:
				self.component.scorecounter.update_score(self.info.score)

		self.component.scoreboard.setscore(self.info.score, self.info.maxcombo)

	def update(self, cur_time):
		if self.info_index >= len(self.resultinfo) or self.resultinfo[self.info_index].time > cur_time:
			return
		while self.info_index < len(self.resultinfo) and self.resultinfo[self.info_index].time < cur_time:
			self.info = self.resultinfo[self.info_index]
			self.process_combo()
			self.process_acc()
			self.info_index += 1
