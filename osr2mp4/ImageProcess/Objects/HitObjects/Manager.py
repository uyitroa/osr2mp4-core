CIRCLE = 0
SLIDER = 1
SPINNER = 2


class HitObjectManager:

	def __init__(self, circle, slider, spinner, maxtimewindow, settings):

		self.settings = settings

		self.circle_manager = circle
		self.slider_manager = slider
		self.spinner_manager = spinner
		self.time_preempt = self.circle_manager.time_preempt
		self.maxtimewindow = maxtimewindow

		self.hitobjects = {}
		self.objtime = []
		self.interval = self.settings.timeframe / self.settings.fps
		self.timer = 0
		self.rate = self.settings.timeframe/1000

		self.objecttype = {
			CIRCLE: [self.circle_manager, self.circle_manager.circles, -self.maxtimewindow - self.interval * 2],
			SLIDER: [self.slider_manager, self.slider_manager.sliders, -175],
			SPINNER: [self.spinner_manager, self.spinner_manager.spinners, -200]}

	def add_slider(self, osu_d, x_pos, y_pos, cur_time):
		self.slider_manager.add_slider(osu_d, x_pos, y_pos, cur_time)

		idd = str(osu_d["id"]) + "s"
		self.hitobjects[idd] = [SLIDER, osu_d["end time"] - cur_time]
		self.objtime.append(idd)

	def add_circle(self, osu_d, x, y, cur_time):
		self.circle_manager.add_circle(osu_d, x, y, cur_time)
		circleduration = osu_d["time"] - cur_time

		idd = str(osu_d["id"]) + "c"
		self.hitobjects[idd] = [CIRCLE, circleduration]
		self.objtime.append(idd)

	def add_spinner(self, osu_d, curtime):
		starttime = osu_d["time"]
		endtime = osu_d["end time"]
		idd = str(osu_d["id"]) + "o"
		self.spinner_manager.add_spinner(osu_d, curtime)
		self.hitobjects[idd] = [SPINNER, endtime - curtime]
		self.objtime.append(idd)

	def delete_circle(self, idd):
		self.hitobjects[idd][1] = -self.maxtimewindow - self.interval * 2

	def fadeout_circle(self, idd):
		self.hitobjects[idd][1] = -self.maxtimewindow - self.interval * 2 + 175
		self.circle_manager.circles[idd][8] = 1

	def notelock_circle(self, idd):
		self.circle_manager.circles[idd][9] = 1

	def sliderchangestate(self, followappear, idd):
		index_interval = 0.65
		if self.slider_manager.sliders[idd].sliderf_i != self.slider_manager.slidermax_index:
			self.slider_manager.sliders[idd].sliderf_i = 0

		if followappear:
			index_interval = -0.65
			self.slider_manager.sliders[idd].sliderf_i = self.slider_manager.slidermax_index - 3

		self.slider_manager.sliders[idd].appear_f = index_interval

	def slidertouchtick(self, idd):
		self.slider_manager.sliders[idd].sliderf_i = 1
		self.slider_manager.sliders[idd].appear_f = -0.1

	# manager of circle add_to_frame and slider add_to_frame
	def add_to_frame(self, background, _):
		i = len(self.objtime)
		while i > 0:  # > 0 because we do i-=1 at the beginning so if it's > -1 it would be "out of range"
			i -= 1

			key = self.objtime[i]

			self.hitobjects[key][1] -= self.interval
			hitobj = self.objecttype[self.hitobjects[key][0]]

			if self.hitobjects[key][1] <= hitobj[2]:

				del hitobj[1][key]

				if self.hitobjects[key][0] == SLIDER:
					del self.slider_manager.arrows[key]

				del self.hitobjects[key]
				del self.objtime[i]
				continue

			hitobj[0].add_to_frame(background, key, _)
