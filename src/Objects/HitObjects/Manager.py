

class HitObjectManager:
	def __init__(self, circle, slider, spinner, maxtimewindow):

		self.preparecircle = circle
		self.prepareslider = slider
		self.preparespinner = spinner
		self.time_preempt = self.preparecircle.time_preempt
		self.maxtimewindow = maxtimewindow

		self.hitobjects = {}
		self.objtime = []
		self.interval = 1000 / 60
		self.CIRCLE = 0
		self.SLIDER = 1
		self.SPINNER = 2

	def add_slider(self, osu_d, x_pos, y_pos, cur_time):
		self.prepareslider.add_slider(osu_d, x_pos, y_pos, cur_time)

		timestamp = str(osu_d["time"]) + "s"
		self.hitobjects[timestamp] = [self.SLIDER, osu_d["end time"] - cur_time]
		self.objtime.append(timestamp)

	def add_circle(self, x, y, cur_time, osu_d):
		self.preparecircle.add_circle(x, y, cur_time, osu_d)
		circleduration = osu_d["time"] - cur_time

		timestamp = str(osu_d["time"]) + "c"
		self.hitobjects[timestamp] = [self.CIRCLE, circleduration]
		self.objtime.append(timestamp)

	def add_spinner(self, starttime, endtime, curtime):
		timestamp = str(starttime) + "o"
		self.preparespinner.add_spinner(starttime, endtime, curtime)
		self.hitobjects[timestamp] = [self.SPINNER, endtime - curtime]
		self.objtime.append(timestamp)

	def delete_circle(self, timestamp):
		self.hitobjects[timestamp][1] = -self.maxtimewindow - self.interval*2

	def fadeout_circle(self, timestamp):
		self.hitobjects[timestamp][1] = -self.maxtimewindow - self.interval * 2 + 175
		self.preparecircle.circles[timestamp][8] = 1

	def notelock_circle(self, timestamp):
		self.preparecircle.circles[timestamp][9] = 1

	def sliderchangestate(self, followappear, timestamp):
		index_interval = 0.65

		if self.prepareslider.sliders[timestamp][6] != self.prepareslider.slidermax_index:
			self.prepareslider.sliders[timestamp][6] = 0

		if followappear:
			index_interval = -0.65
			self.prepareslider.sliders[timestamp][6] = self.prepareslider.slidermax_index - 3

		self.prepareslider.sliders[timestamp][11] = index_interval

	# manager of circle add_to_frame and slider add_to_frame
	def add_to_frame(self, background):
		i = len(self.objtime)
		objecttype = {self.CIRCLE: [self.preparecircle, self.preparecircle.circles, -self.maxtimewindow - self.interval*2],
		              self.SLIDER: [self.prepareslider, self.prepareslider.sliders, -175],
		              self.SPINNER: [self.preparespinner, self.preparespinner.spinners, -200]}
		while i > 0:  # > 0 because we do i-=1 at the beginning so if it's > -1 it would be "out of range"
			i -= 1
			key = self.objtime[i]
			self.hitobjects[key][1] -= self.interval
			hitobj = objecttype[self.hitobjects[key][0]]
			if self.hitobjects[key][1] <= hitobj[2]:
				del hitobj[1][key]
				if self.hitobjects[key][0] == self.SLIDER:
					del self.prepareslider.arrows[key]
				del self.hitobjects[key]
				del self.objtime[i]
				continue
			hitobj[0].add_to_frame(background, key, len(self.objtime) == 1)
