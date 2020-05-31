from ..FrameObject import FrameObject
import numpy as np
from recordclass import recordclass
from ...PrepareFrames.Components.Followpoints import prepare_fp

followpoints = "followpoint"


Fp = recordclass("Fp", "object x y x_vector y_vector t1 t2 spacing")


class Followpoint(FrameObject):
	def __init__(self, frames, scale, movedown, moveright):
		super().__init__(frames)
		self.pointdistance = 32
		self.alpha_tdelta = 200
		self.pointdistance = 32
		self.scale = scale
		self.movedown = movedown
		self.moveright = moveright
		self.preempt = 800

	def add_to_frame(self, background, f_info, to_delete, cur_time):
		d = self.pointdistance * 1.5
		duration = f_info.t2 - f_info.t1
		while d < f_info.spacing - self.pointdistance:
			fraction = d / f_info[7]
			fadeouttime = f_info.t1 + fraction * duration + self.alpha_tdelta
			fadeintime = fadeouttime - self.preempt

			if cur_time < fadeintime:  # too early to draw followpoint
				break
			if cur_time > fadeouttime:  # timeout
				d += self.pointdistance
				if d >= f_info.spacing - self.pointdistance:
					to_delete.append(1)
				continue

			x = f_info.x + fraction * f_info.x_vector
			x = int(x * self.scale) + self.moveright
			y = f_info.y + fraction * f_info.y_vector
			y = int(y * self.scale) + self.movedown

			# quick maths
			alpha = min(1, (cur_time - fadeintime) / self.alpha_tdelta, (fadeouttime - cur_time) / self.alpha_tdelta)

			total_time = fadeouttime - fadeintime
			cur_time_gone = cur_time - fadeintime
			self.frame_index = int(cur_time_gone * (len(self.frames)) / total_time)
			if self.frame_index >= len(self.frames):
				self.frame_index -= len(self.frames)

			super().add_to_frame(background, x, y, alpha=alpha)
			d += self.pointdistance


class FollowPointsManager:
	def __init__(self, fp, settings):
		self.settings = settings
		self.followpoints = []
		self.pointdistance = 32
		self.alpha_tdelta = 200
		self.scale = self.settings.playfieldscale
		self.movedown = self.settings.movedown
		self.moveright = self.settings.moveright
		self.preempt = 800
		self.fp = fp

	def add_fp(self, x1, y1, t1, next_object):
		x2, y2, t2 = next_object["x"], next_object["y"], next_object["time"]

		spacing = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
		if spacing - self.pointdistance < self.pointdistance * 1.5:  # basically if spacing < 81
			return
		x_vector, y_vector = x2 - x1, y2 - y1
		angle = -np.arctan2(y_vector, x_vector) * 180 / np.pi

		# for x in range(self.fp.n_frame):
		# 		self.followpoints[-1][0].append(self.fp[x].rotate(angle))
		fp = prepare_fp(self.fp, angle)
		my_fp = Followpoint(fp, self.scale, self.movedown, self.moveright)
		self.followpoints.append(Fp(my_fp, x1, y1, x_vector, y_vector, t1, t2, int(spacing)))

	def add_to_frame(self, background, cur_time):
		i = len(self.followpoints) - 1
		while i > -1:
			to_delete = []
			self.followpoints[i].object.add_to_frame(background, self.followpoints[i], to_delete, cur_time)
			if to_delete:
				del self.followpoints[i]
				break
			i -= 1
