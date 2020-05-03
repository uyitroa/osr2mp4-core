import time

CIRCLE = 0
SLIDER = 1
SPINNER = 2


class HitObjectManager:

	def __init__(self, circle, slider, spinner, maxtimewindow, settings):

		self.circle_manager = circle
		self.slider_manager = slider
		self.spinner_manager = spinner
		self.time_preempt = self.circle_manager.time_preempt
		self.maxtimewindow = maxtimewindow

		self.hitobjects = {}
		self.objtime = []
		self.interval = settings.timeframe / settings.fps
		self.timer = 0

		self.objecttype = {
			CIRCLE: [self.circle_manager, self.circle_manager.circles, -self.maxtimewindow - self.interval * 2],
			SLIDER: [self.slider_manager, self.slider_manager.sliders, -175],
			SPINNER: [self.spinner_manager, self.spinner_manager.spinners, -200]}

	def add_slider(self, osu_d, x_pos, y_pos, cur_time):
		self.slider_manager.add_slider(osu_d, x_pos, y_pos, cur_time)

		timestamp = str(osu_d["time"]) + "s"
		self.hitobjects[timestamp] = [SLIDER, osu_d["end time"] - cur_time]
		self.objtime.append(timestamp)

	def add_circle(self, x, y, cur_time, osu_d):
		self.circle_manager.add_circle(x, y, cur_time, osu_d)
		circleduration = osu_d["time"] - cur_time

		timestamp = str(osu_d["time"]) + "c"
		self.hitobjects[timestamp] = [CIRCLE, circleduration]
		self.objtime.append(timestamp)

	def add_spinner(self, starttime, endtime, curtime):
		timestamp = str(starttime) + "o"
		self.spinner_manager.add_spinner(starttime, endtime, curtime)
		self.hitobjects[timestamp] = [SPINNER, endtime - curtime]
		self.objtime.append(timestamp)

	def delete_circle(self, timestamp):
		self.hitobjects[timestamp][1] = -self.maxtimewindow - self.interval * 2

	def fadeout_circle(self, timestamp):
		self.hitobjects[timestamp][1] = -self.maxtimewindow - self.interval * 2 + 175
		self.circle_manager.circles[timestamp][8] = 1

	def notelock_circle(self, timestamp):
		self.circle_manager.circles[timestamp][9] = 1

	def sliderchangestate(self, followappear, timestamp):
		index_interval = 0.65

		if self.slider_manager.sliders[timestamp].sliderb_i != self.slider_manager.slidermax_index:
			self.slider_manager.sliders[timestamp].sliderb_i = 0

		if followappear:
			index_interval = -0.65
			self.slider_manager.sliders[timestamp].sliderb_i = self.slider_manager.slidermax_index - 3

		self.slider_manager.sliders[timestamp].appear_f = index_interval

	# manager of circle add_to_frame and slider add_to_frame
	def add_to_frame(self, background):
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

			hitobj[0].add_to_frame(background, key, len(self.objtime) == 1)
