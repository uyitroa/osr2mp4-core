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
		self.hitobjects = []
		self.fadeoutobjects = []
		self.interval = 1000 / 60
		self.CIRCLE = 0
		self.SLIDER = 1

		self.circleindices = []
		self.sliderindices = []
		self.hitobj_size = 0
		self.deleted = 0

	def add_slider(self, osu_d, x_pos, y_pos, beat_duration, duration):
		self.sliderindices.append(self.hitobj_size)
		self.hitobj_size += 1
		self.prepareslider.add_slider(osu_d, x_pos, y_pos, beat_duration, duration)
		pixel_length, color = osu_d["pixel_length"], osu_d["combo_color"]
		sliderduration = beat_duration * pixel_length / (100 * self.diff["SliderMultiplier"]) * osu_d["repeated"]
		self.hitobjects.append([self.SLIDER, sliderduration + duration])

	def add_circle(self, x, y, combo_color, combo_number,  duration, object_type=0):
		self.circleindices.append(self.hitobj_size)
		self.hitobj_size += 1
		self.preparecircle.add_circle(x, y, combo_color, combo_number, duration, object_type)
		circleduration = duration
		self.hitobjects.append([self.CIRCLE, circleduration])

	def circleclicked(self, score):
		if len(self.circleindices) == 0:
			return
		poop = self.hitobjects.pop(self.circleindices[0]-self.deleted)
		print(poop[1])
		if score > 0:
			self.fadeoutobjects.append(poop)
			self.fadeoutobjects[-1][1] = 0
			self.preparecircle.circles[0][8] = 1
		else:
			del self.preparecircle.circles[0]
		del self.circleindices[0]
		self.deleted += 1

	# manager of circle add_to_frame and slider add_to_frame
	def add_to_frame(self, background):
		# print(self.circleindices, self.deleted, self.hitobj_size)
		slider_index = len(self.prepareslider.sliders)
		circle_index = len(self.preparecircle.circles)
		i = len(self.hitobjects)

		sliderwait_multiplier = 10
		circlewait_multiplier = 10

		objecttype = {self.CIRCLE: [circle_index, self.preparecircle, self.preparecircle.circles, circlewait_multiplier],
		              self.SLIDER: [slider_index, self.prepareslider, self.prepareslider.sliders, sliderwait_multiplier]}

		while i > 0:  # > 0 because we do i-=1 at the beginning so if it's > -1 it would be "out of range"
			i -= 1
			self.hitobjects[i][1] -= self.interval
			hitobj = objecttype[self.hitobjects[i][0]]
			index = hitobj[0] = hitobj[0] - 1
			if self.hitobjects[i][0] == self.SLIDER:
				if self.hitobjects[i][1] <= 0:
					self.fadeoutobjects.append(self.hitobjects.pop(i))
					del self.sliderindices[0]
					self.deleted += 1
					continue
			hitobj[1].add_to_frame(background, index)


		i = len(self.fadeoutobjects)
		while i > 0:
			i -= 1
			self.fadeoutobjects[i][1] -= self.interval
			hitobj = objecttype[self.fadeoutobjects[i][0]]
			index = hitobj[0] = hitobj[0] - 1
			if self.fadeoutobjects[i][1] <= -self.interval * 10:  # hitobj[3]:
				del hitobj[2][index]
				if self.fadeoutobjects[i][0] == self.SLIDER:
					del self.prepareslider.arrows[index]
				del self.fadeoutobjects[i]
				continue
			hitobj[1].add_to_frame(background, index)

