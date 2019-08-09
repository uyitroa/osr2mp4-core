class Updater:
	def __init__(self, resultinfo, component, playfieldscale, movedown, moveright):
		self.resultinfo = resultinfo
		self.component = component
		self.info_index = 0
		self.playfieldscale = playfieldscale
		self.movedown = movedown
		self.moveright = moveright

	def process_combo(self):
		if self.info.combostatus == 1:
			self.component.combocounter.add_combo()
		elif self.info.combostatus == -1:
			self.component.combocounter.breakcombo()

	def process_acc(self):
		objtype = type(self.info.more).__name__
		if objtype == "Circle":
			timestamp = str(self.info.timestamp) + "c"
			x, y = self.info.more.x, self.info.more.y
			if self.info.more.state == 1:
				self.component.hitobjmanager.notelock_circle(timestamp)
			elif self.info.more.state == 2:
				self.component.hitobjmanager.fadeout_circle(timestamp)
				self.component.urbar.add_bar(self.info.more.deltat, self.info.hitresult)
				if self.info.more.sliderhead:
					self.component.hitobjmanager.sliderchangestate(self.info.more.followstate,
					                                               str(self.info.timestamp) + "s")

		elif objtype == "Slider":
			timestamp = str(self.info.timestamp) + "s"
			x, y = self.info.more.x, self.info.more.y
			followbit = self.info.more.followstate
			if int(followbit[0]):
				self.component.hitobjmanager.sliderchangestate(int(followbit[1]), timestamp)
			self.component.scorecounter.bonus_score(self.info.more.hitvalue)

		else:
			timestamp = str(self.info.timestamp) + "o"
			x, y = 384 * 0.5, 512 * 0.5
			self.component.spinner.update_spinner(timestamp, self.info.more.rotate, self.info.more.progress)
			self.component.scorecounter.bonus_score(self.info.more.hitvalue)
			if self.info.more.bonusscore >= 1:
				self.component.spinbonus.set_bonusscore(self.info.more.bonusscore)

		x = int(x * self.playfieldscale + self.moveright)
		y = int(y * self.playfieldscale + self.movedown)

		if self.info.hitresult is not None:
			if not (objtype == "Circle" and self.info.more.sliderhead):
				self.component.hitresult.add_result(self.info.hitresult, x, y)
			if objtype != "Slider" or self.info.more.tickend:
				self.component.scorecounter.update_score(self.component.combocounter.get_combo(), self.info.hitresult)


	def update(self, cur_time):
		self.info = self.resultinfo[self.info_index]
		if self.info.time > cur_time:
			return

		self.process_combo()
		self.process_acc()
		self.info_index += 1
