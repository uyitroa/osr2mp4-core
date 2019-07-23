from Objects.Circles import PrepareCircles
from Objects.Slider import PrepareSlider


class HitObjectManager:
	def __init__(self, slider_combo, path, diff, scale, maxcombo, gap, colors, movedown, moveright):
		self.preparecircle = PrepareCircles(slider_combo, path, diff, scale, maxcombo, gap, colors)
		self.time_preempt = self.preparecircle.time_preempt
		opacity = self.preparecircle.opacity_interval
		self.prepareslider = PrepareSlider(path, diff, self.time_preempt, opacity, scale, colors, movedown, moveright)
		self.hitobject = []
		self.interval = 1000 / 60
		self.CIRCLE = 0
		self.SLIDER = 1

	def add_slider(self, osu_d, x_pos, y_pos, beat_duration):
		self.prepareslider.add_slider(osu_d, x_pos, y_pos, beat_duration)
		sliderduration = (self.prepareslider.sliders[-1][3]-self.time_preempt) * self.prepareslider.sliders[-1][10] + self.time_preempt  # cause slidersduration would have self.time_preempt * repeated
		self.hitobject.append([self.SLIDER, sliderduration])

	def add_circle(self, x, y, combo_color, combo_number,  object_type=0):
		self.preparecircle.add_circle(x, y, combo_color, combo_number,  object_type)
		circleduration = self.time_preempt
		self.hitobject.append([self.CIRCLE, circleduration])

	# manager of circle add_to_frame and slider add_to_frame
	def add_to_frame(self, background):
		slider_index = len(self.prepareslider.sliders)
		circle_index = len(self.preparecircle.circles)
		i = len(self.hitobject)

		sliderwait_multiplier = 10
		circlewait_multiplier = 14

		objecttype = {self.CIRCLE: [circle_index, self.preparecircle, self.preparecircle.circles, circlewait_multiplier],
		              self.SLIDER: [slider_index, self.prepareslider, self.prepareslider.sliders, sliderwait_multiplier]}

		while i > 0:  # > 0 because we do i-=1 at the beginning so if it's > -1 it would be "out of range"
			i -= 1
			self.hitobject[i][1] -= self.interval
			hitobj = objecttype[self.hitobject[i][0]]
			index = hitobj[0] = hitobj[0] - 1
			if self.hitobject[i][1] < -self.interval * hitobj[3]:  # for late click and effect instead of < 0
				del hitobj[2][index]
				if self.hitobject[i][0] == self.SLIDER:
					del self.prepareslider.arrows[index]
				del self.hitobject[i]
				continue
			hitobj[1].add_to_frame(background, index)
