from Objects.abstracts import *


class ScoreCounter(Images):
	def __init__(self, scorenumbers, diff, width, height, gap, scale, draw=True):
		self.draw = draw
		self.showscore = 0
		self.score = 0
		self.diff = diff
		self.diff_multiplier = self.difficulty_multiplier()
		if draw:
			self.score_images = scorenumbers.score_images
			self.prepare_number()
			self.width = width
			self.height = height
			self.gap = int(gap * scale * 0.75)
			self.divide_by_255 = 1 / 255.0

	def prepare_number(self):
		for image in self.score_images:
			image.change_size(0.75, 0.75)

	def difficulty_multiplier(self):
		points = self.diff["OverallDifficulty"] + self.diff["HPDrainRate"] + self.diff["CircleSize"]
		if points in range(0, 6):
			return 2
		if points in range(6, 13):
			return 3
		if points in range(13, 18):
			return 4
		if points in range(18, 25):
			return 5
		return 6

	def update_score(self, combo, hitvalue, mod=1):
		self.score += int(hitvalue + (hitvalue * ((combo * self.diff_multiplier * mod) / 25)))

	def bonus_score(self, score):
		self.score += score
		self.showscore += score

	def add_to_frame(self, background):
		if self.draw:
			score_string = str(int(self.showscore))
			score_string = "0" * (8 - len(score_string)) + score_string
			x = self.width - (-self.gap + self.score_images[0].img.shape[1]) * len(score_string)
			y = self.score_images[0].img.shape[0]//2
			for digit in score_string:
				digit = int(digit)
				self.img = self.score_images[digit].img
				super().add_to_frame(background, x, y)
				x += -self.gap + self.score_images[0].img.shape[1]


		add_up = max(7.27, (self.score - self.showscore)/12.72)
		if self.showscore + add_up > self.score:
			self.showscore = min(self.score, max(self.score - 1, self.showscore + 0.05))
		else:
			self.showscore += add_up

