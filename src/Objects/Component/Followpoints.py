from Objects.abstracts import *
import os.path


followpoints = "followpoint"


class FollowPointsManager(Images):
	def __init__(self, path, scale, movedown, moveright):
		self.followpoints = []
		self.pointdistance = 32
		self.alpha_tdelta = 200
		self.scale = scale
		self.movedown = movedown
		self.moveright = moveright
		self.preempt = 800
		self.fp = AnimatableImage(path, followpoints, scale * 0.5, True, "-", 1)

	def add_fp(self, x1, y1, t1, next_object):
		x2, y2, t2 = next_object["x"], next_object["y"], next_object["time"]

		spacing = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
		if spacing - self.pointdistance < self.pointdistance * 1.5:  # basically if spacing < 81
			return
		x_vector, y_vector = x2 - x1, y2 - y1
		angle = -np.arctan2(y_vector, x_vector) * 180 / np.pi
		self.followpoints.append([[], x1, y1, x_vector, y_vector, t1, t2, int(spacing)])

		for x in range(self.fp.n_frame):
				self.followpoints[-1][0].append(self.fp.image_at(x).rotate_image(angle))

	def add_to_frame(self, background, cur_time):
		i = len(self.followpoints) - 1
		while i > -1:
			d = self.pointdistance * 1.5
			duration = self.followpoints[i][6] - self.followpoints[i][5]
			to_delete = False
			while d < self.followpoints[i][7] - self.pointdistance:
				fraction = d/self.followpoints[i][7]
				fadeouttime = self.followpoints[i][5] + fraction * duration + self.alpha_tdelta
				fadeintime = fadeouttime - self.preempt

				if cur_time < fadeintime:  # too early to draw followpoint
					break
				if cur_time > fadeouttime:  # timeout
					d += self.pointdistance
					to_delete = d >= self.followpoints[i][7] - self.pointdistance
					continue


				x = self.followpoints[i][1] + fraction * self.followpoints[i][3]
				x = int(x * self.scale) + self.moveright
				y = self.followpoints[i][2] + fraction * self.followpoints[i][4]
				y = int(y * self.scale) + self.movedown

				# quick maths
				alpha = min(1, (cur_time - fadeintime)/self.alpha_tdelta, (fadeouttime - cur_time)/self.alpha_tdelta)

				total_time = fadeouttime - fadeintime
				cur_time_gone = cur_time - fadeintime
				index = int(cur_time_gone * (len(self.followpoints[i][0]))/total_time)
				if index >= len(self.followpoints[i][0]):
					index -= len(self.followpoints[i][0])

				self.img = self.followpoints[i][0][index][:, :, :] * alpha
				super().add_to_frame(background, x, y)
				d += self.pointdistance
			if to_delete:
				del self.followpoints[i]
				break
			i -= 1
