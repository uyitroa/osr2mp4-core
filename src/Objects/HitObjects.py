from Objects.Circles import PrepareCircles
from Objects.Slider import PrepareSlider


class HitObjectManager:
	def __init__(self, slider_combo, path, diff, scale, maxcombo, gap, colors, movedown, moveright):
		self.preparecircle = PrepareCircles(slider_combo, path, diff, scale, maxcombo, gap, colors)
		self.time_preempt = self.preparecircle.time_preempt
		opacity = self.preparecircle.opacity_interval
		self.diff = diff
		self.maxtimewindow = 150 + 50 * (5 - diff["OverallDifficulty"]) / 5
		self.prepareslider = PrepareSlider(path, diff, self.time_preempt, opacity, scale, colors, movedown, moveright)
		self.hitobjects = {}
		self.objtime = []
		self.interval = 1000 / 60
		self.CIRCLE = 0
		self.SLIDER = 1

	def add_slider(self, osu_d, x_pos, y_pos, cur_time, timestamp):
		self.prepareslider.add_slider(osu_d, x_pos, y_pos, cur_time, timestamp)

		timestamp = str(timestamp) + "s"
		self.hitobjects[timestamp] = [self.SLIDER, osu_d["end time"] - cur_time, len(self.objtime)]
		self.objtime.append(timestamp)

	def add_circle(self, x, y, combo_color, combo_number, duration, timestamp, object_type=0):
		self.preparecircle.add_circle(x, y, combo_color, combo_number, duration, timestamp, object_type)
		circleduration = duration

		timestamp = str(timestamp) + "c"
		self.hitobjects[timestamp] = [self.CIRCLE, circleduration, len(self.objtime)]
		self.objtime.append(timestamp)

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
	def add_to_frame(self, background):
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

		for i in range(len(self.objtime)):
			self.hitobjects[self.objtime[i]][2] = i
