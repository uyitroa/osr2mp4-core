from Objects.abstracts import *


class CircleManager(Images):
	def __init__(self, frames, timepreempt):
		self.slidercircle_frames, self.circle_frames, self.circle_fadeout = frames
		self.time_preempt = timepreempt
		self.interval = 1000/60
		self.circles = {}

	def add_circle(self, x, y, cur_time, osu_d):
		combo_color, combo_number = osu_d["combo_color"], osu_d["combo_number"]
		duration = osu_d["time"] - cur_time
		object_type = "slider" in osu_d["type"]
		start_index = int((self.time_preempt - duration)/self.interval + 0.5) - 1
		# x, y, duration, frame index, color, combo number, obj type, fade out index, fadeout bool, x step, max step
		self.circles[str(osu_d["time"]) + "c"] = [x, y, duration, start_index, combo_color, combo_number, object_type, 0, 0, 0, 0]

	def add_to_frame(self, background, i, _):
		color = self.circles[i][4] - 1
		self.circles[i][2] -= self.interval

		# timeout for circle, if self.interval*4 is the time for circle fadeout effect
		if self.circles[i][8]:
			isslider = self.circles[i][6]
			if self.circles[i][7] > len(self.circle_fadeout[isslider][color]) - 1:
				return
			self.buf = self.circle_fadeout[isslider][color][self.circles[i][7]]
			self.circles[i][7] += 1
			super().add_to_frame(background, self.circles[i][0], self.circles[i][1])
			return

		self.circles[i][3] += 1
		number = self.circles[i][5]

		# notelock
		if self.circles[i][9]:
			step = 1 if self.circles[i][10] % 2 == 0 else -1
			self.circles[i][9] += step * 5
			if self.circles[i][9] == 1 and self.circles[i][10] == 5:
				self.circles[i][9] = 0
			elif self.circles[i][9]-1 == step * 10:
				self.circles[i][10] += 1


		if self.circles[i][6]:
			# in case opacity_index exceed list range because of the creator shitty algorithm
			# the creator is me btw
			opacity_index = min(self.circles[i][3], len(self.slidercircle_frames[color][number]) - 1)
			self.buf = self.slidercircle_frames[color][number][opacity_index]
		else:
			opacity_index = min(self.circles[i][3], len(self.circle_frames[color][number - 1]) - 1)
			self.buf = self.circle_frames[color][number - 1][opacity_index]

		# if self.circles[i][6] and self.circles[i][2] <= 0:
		# 	self.img[:, :, :] = self.img[:, :, :] * max(0, 1+self.circles[i][2]/50)

		super().add_to_frame(background, self.circles[i][0]+self.circles[i][9], self.circles[i][1])
