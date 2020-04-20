from Objects.abstracts import *

hitprefix = "hit"


class HitResult(Images):
	def __init__(self, path, scale, playfieldscale, accuracy):
		self.accuracy = accuracy
		self.scores_images = {}
		self.scores_frames = {}
		self.divide_by_255 = 1 / 255.0
		self.hitresults = []
		self.interval = 1000 / 60
		self.time = 600
		self.playfieldscale = playfieldscale
		for x in [0, 50, 100]:
			self.scores_images[x] = Images(path + hitprefix + str(x), scale, rotate=x == 0)
			self.scores_frames[x] = []
		self.prepare_frames()

	def prepare_frames(self):
		for x in self.scores_images:
			end = 175
			start = 125
			if x != 0:
				end = 100
				start = 70
				for y in range(start, end, -5):
					self.scores_images[x].change_size(y / 100, y / 100)
					self.scores_frames[x].append(self.scores_images[x].img)

			for y in range(end, start, -2):
				self.scores_images[x].change_size(y / 100, y / 100)
				img = self.scores_images[x].img
				if x == 0:
					img = img.rotate(-10 - (end - y) / 10)
				self.scores_frames[x].append(img)

	def add_result(self, scores, x, y):
		self.accuracy.update_acc(scores)
		if scores == 300:
			return
		# [score, x, y, index, alpha, time, go down]
		self.hitresults.append([scores, x, y, 0, 20, 0, 3])

	def add_to_frame(self, background):
		i = len(self.hitresults)
		while i > 0:
			i -= 1
			if self.hitresults[i][5] >= self.time:
				del self.hitresults[i]
				break

			score = self.hitresults[i][0]
			self.img = super().newalpha(self.scores_frames[score][self.hitresults[i][3]], self.hitresults[i][4] / 100)

			x, y = self.hitresults[i][1], self.hitresults[i][2]
			super().add_to_frame(background, x, y)

			if score == 0:
				self.hitresults[i][2] += int(self.hitresults[i][6] * self.playfieldscale)
				self.hitresults[i][6] = max(0.8, self.hitresults[i][6] - 0.2)
			self.hitresults[i][3] = min(len(self.scores_frames[score]) - 1, self.hitresults[i][3] + 1)
			self.hitresults[i][5] += self.interval
			if self.hitresults[i][5] >= self.time - self.interval * 10:
				self.hitresults[i][4] = max(0, self.hitresults[i][4] - 10)
			else:
				self.hitresults[i][4] = min(100, self.hitresults[i][4] + 20)
	# cv2.putText(background, str(self.total), (200, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1,
	#             lineType=cv2.LINE_AA)
