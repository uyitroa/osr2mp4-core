from Objects.abstracts import *


hitprefix = "hit"


class HitResult(Images):
	def __init__(self, path, scale):
		self.scores_images = {}
		self.scores_frames = {}
		self.divide_by_255 = 1/255.0
		self.timingscores = []
		self.interval = 1000/60
		self.time = 600
		for x in [0, 50, 100]:
			self.scores_images[x] = Images(path+hitprefix+str(x)+".png", scale)
			if x == 0:
				self.to_square(self.scores_images[x])
			self.scores_images[x].to_3channel()
			self.scores_frames[x] = []
		self.prepare_frames()

	def to_square(self, image):
		max_length = int(np.sqrt(image.img.shape[0]**2 + image.img.shape[1]**2) + 2)  # round but with int
		square = np.zeros((max_length, max_length, image.img.shape[2]))
		y1, y2 = int(max_length / 2 - image.orig_rows / 2), int(max_length / 2 + image.orig_rows / 2)
		x1, x2 = int(max_length / 2 - image.orig_cols / 2), int(max_length / 2 + image.orig_cols / 2)
		square[y1:y2, x1:x2, :] = image.img[:, :, :]
		image.orig_img = square
		image.orig_rows, image.orig_cols = max_length, max_length

	def rotate_image(self, image, angle):
		image_center = tuple(np.array(image.shape[1::-1]) / 2)
		rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
		result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
		return result

	def to_3channel(self, image):
		# convert 4 channel to 3 channel, so we can ignore alpha channel, this will optimize the time of add_to_frame
		# where we needed to do each time alpha_s * img[:, :, 0:3]. Now we don't need to do it anymore
		alpha_s = image[:, :, 3] * self.divide_by_255
		for c in range(3):
			image[:, :, c] = image[:, :, c] * alpha_s

	def prepare_frames(self):
		for x in self.scores_images:
			end = 175
			if x != 0:
				end = 105
				for y in range(50, end, 10):
					self.scores_images[x].change_size(y/100, y/100)
					self.scores_frames[x].append(self.scores_images[x].img)

			for y in range(end, 75, -5):
				self.scores_images[x].change_size(y/100, y/100)
				img = self.scores_images[x].img
				if x == 0:
					img = self.rotate_image(img, -10)
				self.scores_frames[x].append(img)

	def add_timingscores(self, scores, x, y):
		if scores == 300:
			return
		# [score, x, y, index, alpha, time, go down]
		self.timingscores.append([scores, x, y, 0, 20, 0, 7])

	def add_to_frame(self, background):
		i = len(self.timingscores)
		while i > 0:
			i -= 1
			if self.timingscores[i][5] >= self.time:
				del self.timingscores[i]
				break

			score = self.timingscores[i][0]
			self.img = self.scores_frames[score][self.timingscores[i][3]][:, :, :] * (self.timingscores[i][4]/100)

			x, y = self.timingscores[i][1], self.timingscores[i][2]
			super().add_to_frame(background, x, y)

			if score == 0:
				self.timingscores[i][2] += int(self.timingscores[i][6])
				self.timingscores[i][6] = max(2, self.timingscores[i][6] - 0.5)
			self.timingscores[i][3] = min(len(self.scores_frames[score])-1, self.timingscores[i][3]+1)
			self.timingscores[i][5] += self.interval
			if self.timingscores[i][5] >= self.time - self.interval * 10:
				self.timingscores[i][4] = max(0, self.timingscores[i][4]-10)
			else:
				self.timingscores[i][4] = min(100, self.timingscores[i][4]+20)
