from Objects.abstracts import *
import os.path


class Fp(Images):
	def __init__(self, filename, scale):
		Images.__init__(self, filename)
		self.to_square()
		self.change_size(scale * 0.5, scale * 0.5)
		self.orig_img = np.copy(self.img)
		self.orig_rows = self.orig_img.shape[0]
		self.orig_cols = self.orig_img.shape[1]
		self.to_3channel()

	def to_square(self):
		max_length = int(np.sqrt(self.img.shape[0]**2 + self.img.shape[1]**2) + 2)  # round but with int
		square = np.zeros((max_length, max_length, self.img.shape[2]))
		y1, y2 = int(max_length / 2 - self.orig_rows / 2), int(max_length / 2 + self.orig_rows / 2)
		x1, x2 = int(max_length / 2 - self.orig_cols / 2), int(max_length / 2 + self.orig_cols / 2)
		square[y1:y2, x1:x2, :] = self.img[:, :, :]
		self.orig_img = square
		self.orig_rows, self.orig_cols = max_length, max_length
		# cv2.imwrite("test.png", self.orig_img)
		# cv2.yes

	def rotate_image(self, angle):
		image_center = tuple(np.array(self.img.shape[1::-1]) / 2)
		rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
		result = cv2.warpAffine(self.img, rot_mat, self.img.shape[1::-1], flags=cv2.INTER_LINEAR)
		return result


class FollowPointsManager(Images):
	def __init__(self, filename, scale, movedown, moveright):
		self.fp_frames = []
		self.followpoints = []
		self.pointdistance = 32
		self.scale = scale
		self.movedown = movedown
		self.moveright = moveright
		self.preempt = 800
		self.alpha_tdelta = 200
		self.divide_by_255 = 1/255.0
		counter = 0
		should_continue = True
		fp = None
		while should_continue:
			self.fp_frames.append(fp)
			fp = Fp(filename + "-" + str(counter) + ".png", scale)
			counter += 1
			should_continue = os.path.isfile(filename + "-" + str(counter) + ".png")
		self.fp_frames.pop(0)
		self.img = np.zeros(self.fp_frames[0].orig_img.shape)

	def add_fp(self, x1, y1, t1, next_object, simulate_endtime):
		x2, y2, t2 = next_object["x"], next_object["y"], next_object["time"]

		spacing = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
		if spacing - self.pointdistance < self.pointdistance * 1.5:  # basically if spacing < 81
			return
		x_vector, y_vector = x2 - x1, y2 - y1
		angle = -np.arctan2(y_vector, x_vector) * 180 / np.pi
		self.followpoints.append([[], x1, y1, x_vector, y_vector, t1, t2, int(spacing)])

		if t2 + self.alpha_tdelta < simulate_endtime:
			empty = np.zeros((1, 1, 4))
		for x in range(len(self.fp_frames)):
			if t2 + self.alpha_tdelta < simulate_endtime:
				self.followpoints[-1][0].append(empty)
			else:
				self.followpoints[-1][0].append(self.fp_frames[x].rotate_image(angle))

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
