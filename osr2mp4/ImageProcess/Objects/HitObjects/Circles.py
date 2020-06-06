from recordclass import recordclass

from ... import imageproc
from ..FrameObject import FrameObject

Circle = recordclass("Circle", "x y duration frame_i color combo_n obj_type fadeout_i is_fadeout x_step max_step")


class CircleManager(FrameObject):
	def __init__(self, frames, timepreempt, number, settings):
		self.settings = settings
		self.slidercircle_frames, self.circle_frames, self.circle_fadeout, self.alphas = frames
		self.number = number
		self.time_preempt = timepreempt
		self.interval = self.settings.timeframe / self.settings.fps
		self.circles = {}

		self.timer = 0

	def add_circle(self, osu_d, x, y, cur_time):

		combo_color, combo_number = osu_d["combo_color"], osu_d["combo_number"]

		object_type = "slider" in osu_d["type"]

		duration = osu_d["time"] - cur_time
		start_index = int((self.time_preempt - duration)/self.interval + 0.5) - 1

		key = str(osu_d["id"]) + "c"
		self.circles[key] = Circle(x, y, duration, start_index, combo_color, combo_number, object_type, 0, 0, 0, 0)

	def notelock(self, circle):

		step = 1 if circle.max_step % 2 == 0 else -1
		circle.x_step += step * 5

		if circle.x_step == 1 and circle.max_step == 5:
			circle.x_step = 0

		elif circle.x_step - 1 == step * 10:
			circle.max_step += 1

	def getcircle(self, circle):

		color_index = circle.color - 1

		if circle.obj_type:
			# in case opacity_index exceed list range

			opacity_index = min(circle.frame_i, len(self.slidercircle_frames[color_index]) - 1)
			return self.slidercircle_frames[color_index][opacity_index], opacity_index

		else:

			opacity_index = min(circle.frame_i, len(self.circle_frames[color_index]) - 1)
			return self.circle_frames[color_index][opacity_index], opacity_index

	def add_to_frame(self, background, i, _):
		circle = self.circles[i]

		color_index = circle.color - 1
		circle.duration -= self.interval

		# timeout for circle, if self.interval*4 is the time for circle fadeout effect
		if circle.is_fadeout:
			is_slider = circle.obj_type
			fadeout_frames = self.circle_fadeout[is_slider][color_index]

			if circle.fadeout_i > len(fadeout_frames) - 1:
				return

			img = fadeout_frames[circle.fadeout_i]
			imageproc.add(img, background, circle.x, circle.y)

			circle.fadeout_i += 1
			return

		circle.frame_i += 1
		number = circle.combo_n

		# notelock
		if circle.x_step:
			self.notelock(circle)

		img, index = self.getcircle(circle)

		imageproc.add(img, background, circle.x+circle.x_step, circle.y)
		self.number.add_to_frame(background, circle.x+circle.x_step, circle.y, self.alphas[index], number)


