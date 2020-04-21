from recordclass import recordclass

from Objects.abstracts import *


Circle = recordclass("Circle", "x y duration frame_i color combo_n obj_type fadeout_i is_fadeout x_step max_step")


class CircleManager(Images):
	def __init__(self, frames, timepreempt):
		self.slidercircle_frames, self.circle_frames, self.circle_fadeout, self.number = frames
		self.time_preempt = timepreempt
		self.interval = 1000/60
		self.circles = {}

	def add_circle(self, x, y, cur_time, osu_d):
		combo_color, combo_number = osu_d["combo_color"], osu_d["combo_number"]
		duration = osu_d["time"] - cur_time
		object_type = "slider" in osu_d["type"]
		start_index = int((self.time_preempt - duration)/self.interval + 0.5) - 1
		# x, y, duration, frame index, color, combo number, obj type, fade out index, fadeout bool, x step, max step
		self.circles[str(osu_d["time"]) + "c"] = Circle(x, y, duration, start_index, combo_color, combo_number, object_type, 0, 0, 0, 0)

	def add_to_frame(self, background, i, _):
		color = self.circles[i].color - 1
		self.circles[i].duration -= self.interval

		# timeout for circle, if self.interval*4 is the time for circle fadeout effect
		if self.circles[i].is_fadeout:
			isslider = self.circles[i].obj_type
			if self.circles[i].fadeout_i > len(self.circle_fadeout[isslider][color]) - 1:
				return
			self.img = self.circle_fadeout[isslider][color][self.circles[i][7]]
			self.circles[i].fadeout_i += 1
			super().add_to_frame(background, self.circles[i].x, self.circles[i].y)
			return

		self.circles[i].frame_i += 1
		number = self.circles[i].combo_n

		# notelock
		if self.circles[i].x_step:
			step = 1 if self.circles[i].max_step % 2 == 0 else -1
			self.circles[i].x_step += step * 5
			if self.circles[i].x_step == 1 and self.circles[i].max_step == 5:
				self.circles[i].x_step = 0
			elif self.circles[i].x_step-1 == step * 10:
				self.circles[i].max_step += 1


		if self.circles[i].obj_type:
			# in case opacity_index exceed list range because of the creator shitty algorithm
			# the creator is me btw
			opacity_index = min(self.circles[i].frame_i, len(self.slidercircle_frames[color]) - 1)
			self.img = self.slidercircle_frames[color][opacity_index]
		else:
			opacity_index = min(self.circles[i].frame_i, len(self.circle_frames[color]) - 1)
			self.img = self.circle_frames[color][opacity_index]

		# if self.circles[i].obj_type and self.circles[i].duration <= 0:
		# 	self.img[:, :, :] = self.img[:, :, :] * max(0, 1+self.circles[i].duration/50)
		super().add_to_frame(background, self.circles[i].x+self.circles[i].x_step, self.circles[i].y)
		self.number.draw(background, self.circles[i].frame_i, number, self.circles[i].x+self.circles[i].x_step, self.circles[i].y)

