from Objects.Circles import PrepareCircles
from Objects.Slider import PrepareSlider
from Objects.Spinner import PrepareSpinner


class HitObjectManager:
	def __init__(self, slider_combo, path, diff, scale, maxcombo, gap, colors, movedown, moveright, check, timingscore):

		self.preparecircle = PrepareCircles(slider_combo, path, diff, scale, maxcombo, gap, colors)
		self.time_preempt = self.preparecircle.time_preempt
		opacity = self.preparecircle.opacity_interval
		self.diff = diff
		self.maxtimewindow = 150 + 50 * (5 - diff["OverallDifficulty"]) / 5
		self.prepareslider = PrepareSlider(path, diff, self.time_preempt, opacity, scale, colors, movedown, moveright)
		self.preparespinner = PrepareSpinner(diff["OverallDifficulty"], scale, path)
		self.hitobjects = {}
		self.objtime = []
		self.interval = 1000 / 60
		self.CIRCLE = 0
		self.SLIDER = 1
		self.SPINNER = 2

		self.movedown = movedown
		self.moveright = moveright
		self.scale = scale
		self.check = check
		self.timingscore = timingscore

	def add_slider(self, osu_d, x_pos, y_pos, cur_time, timestamp, hitobjindex):
		self.prepareslider.add_slider(osu_d, x_pos, y_pos, cur_time, timestamp)

		timestamp = str(timestamp) + "s"
		self.hitobjects[timestamp] = [self.SLIDER, osu_d["end time"] - cur_time, len(self.objtime), hitobjindex, 1]
		self.objtime.append(timestamp)

	def add_circle(self, x, y, combo_color, combo_number, duration, timestamp, hitobjindex, object_type=0):
		self.preparecircle.add_circle(x, y, combo_color, combo_number, duration, timestamp, object_type)
		circleduration = duration

		timestamp = str(timestamp) + "c"
		self.hitobjects[timestamp] = [self.CIRCLE, circleduration, len(self.objtime), hitobjindex, 1]
		self.objtime.append(timestamp)

	def add_spinner(self, starttime, endtime, curtime, hitobjindex):
		self.preparespinner.add_spinner(starttime, endtime, curtime)
		timestamp = str(starttime) + "o"
		self.hitobjects[timestamp] = [self.SPINNER, endtime - curtime, len(self.objtime), hitobjindex, 1]

	def circleclicked(self, score, timestamp, followappear):
		key = str(timestamp) + "c"
		if self.preparecircle.circles[key][6]:
			self.preparecircle.circles[key][8] = 1
			self.sliderchangestate(followappear, timestamp)
			# del self.objtime[self.hitobjects[key][2]]
			# del self.preparecircle.circles[key]
			# del self.hitobjects[key]
		else:
			if score > 0:
				self.preparecircle.circles[key][8] = 1
			# else:
			# 	del self.objtime[self.hitobjects[key][2]]
			# 	del self.preparecircle.circles[key]
			# 	del self.hitobjects[key]

	def sliderchangestate(self, followappear, timestamp):
		key = str(timestamp) + "s"
		index_interval = 0.65

		if self.prepareslider.sliders[key][6] != self.prepareslider.slidermax_index:
			self.prepareslider.sliders[key][6] = 0

		if followappear:
			index_interval = -0.75
			self.prepareslider.sliders[key][6] = self.prepareslider.slidermax_index - 3

		self.prepareslider.sliders[key][11] = index_interval

	# manager of circle add_to_frame and slider add_to_frame
	def add_to_frame(self, background, osr, new_click):
		i = len(self.objtime)

		objecttype = {self.CIRCLE: [self.preparecircle, self.preparecircle.circles],
		              self.SLIDER: [self.prepareslider, self.prepareslider.sliders]}
		while i > 0:  # > 0 because we do i-=1 at the beginning so if it's > -1 it would be "out of range"
			i -= 1
			key = self.objtime[i]
			self.hitobjects[key][1] -= self.interval
			hitobj = objecttype[self.hitobjects[key][0]]
			if self.hitobjects[key][1] <= -self.interval * 10: # and self.hitobjects[key][0] == self.SLIDER:  # hitobj[3]:
				del hitobj[1][key]
				if self.hitobjects[key][0] == self.SLIDER:
					del self.prepareslider.arrows[key]
				del self.hitobjects[key]
				del self.objtime[i]
				continue
			hitobj[0].add_to_frame(background, key)

		note_lock = False
		for i in range(len(self.objtime)):
			key = str(self.objtime[i])
			self.hitobjects[key][2] = 1
			if self.hitobjects[key][0] == self.CIRCLE and self.hitobjects[key][4]:
				update, score, timestamp, x, y = self.check.checkcircle(self.hitobjects[key][3], osr, new_click)
				if update:
					new_click = max(0, new_click - 1)
					if note_lock:
						self.preparecircle.circles[key][9] = 1
						if score != 0:
							continue
					self.hitobjects[key][4] = 0
					x = int((x * self.scale) + self.moveright)
					y = int((y * self.scale) + self.movedown)
					followappear = False
					if score > 0:
						self.preparecircle.circles[key][8] = 1
						followappear = True
					if self.preparecircle.circles[key][6]:
						self.sliderchangestate(followappear, timestamp)
					else:
						self.timingscore.add_timingscores(score, x, y)
				else:
					note_lock = True
			elif self.hitobjects[key][0] == self.SLIDER and self.hitobjects[key][4]:
				update, score, timestamp, x, y, followappear = self.check.checkslider(self.hitobjects[key][3], osr)
				if update:
					if score is not None:
						self.hitobjects[key][4] = 0
						x = int((x * self.scale) + self.moveright)
						y = int((y * self.scale) + self.movedown)
						self.timingscore.add_timingscores(score, x, y)
					self.sliderchangestate(followappear, timestamp)

			elif self.hitobjects[key][0] == self.SPINNER and self.hitobjects[key][4]:
				pass


