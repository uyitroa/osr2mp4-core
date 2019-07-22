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
		self.IS_CIRCLE = 0
		# self.IS_CIRCLESLIDER = 1
		self.IS_SLIDER = 2

	def add_slider(self, osu_d, x_pos, y_pos, beat_duration):
		self.prepareslider.add_slider(osu_d, x_pos, y_pos, beat_duration)
		sliderduration = self.prepareslider.sliders[-1][3] * self.prepareslider.sliders[-1][10]
		self.hitobject.append([self.IS_SLIDER, sliderduration])

	def add_circle(self, x, y, combo_color, combo_number,  object_type=0):
		self.preparecircle.add_circle(x, y, combo_color, combo_number,  object_type)
		circleduration = self.time_preempt
		self.hitobject.append([self.IS_CIRCLE, circleduration])

	# manager of circle add_to_frame and slider add_to_frame
	def add_to_frame(self, background):
		slider_index = len(self.prepareslider.sliders)
		circle_index = len(self.preparecircle.circles)
		i = len(self.hitobject)

		while i > 0:  # > 0 because we do i-=1 at the beginning so if it's > -1 it would be "out of range"
			i -= 1
			self.hitobject[i][1] -= self.interval
			if self.hitobject[i][0] == self.IS_CIRCLE:
				circle_index -= 1
				if self.hitobject[i][1] < -self.interval * 14:  # for late click
					del self.preparecircle.circles[circle_index]
					del self.hitobject[i]
					# circle_index -= 1
					continue
				self.preparecircle.add_to_frame(background, circle_index)
			else:
				slider_index -= 1
				if self.hitobject[i][1] < -self.interval * 10:  # for effect
					del self.prepareslider.sliders[slider_index]
					del self.hitobject[i]
					# slider_index -= 1
					continue
				self.prepareslider.add_to_frame(background, slider_index)


