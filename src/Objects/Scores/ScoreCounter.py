from Objects.abstracts import *


class ScoreCounter(Images):
	def __init__(self, scorenumbers, diff, width, height, gap, scale, draw=True):
		self.draw = draw
		self.freeze = 0
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
		for i in range(len(self.score_images)):
			self.score_images[i].buf.set(*self.score_images[i].change_size(0.75, 0.75))

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

	def set_score(self, freeze, score, showscore):
		self.freeze = freeze
		self.score = score
		self.showscore = showscore

	def update_score(self, combo, hitvalue, mod=1):
		self.score += int(hitvalue + (hitvalue * ((combo * self.diff_multiplier * mod) / 25)))

	def bonus_score(self, score):
		self.score += score
		self.showscore += score

	def add_to_frame(self, background, cur_time):
		if self.draw:
			score_string = str(int(self.showscore))
			score_string = "0" * (8 - len(score_string)) + score_string
			x = self.width - (-self.gap + self.score_images[0].buf.w) * len(score_string)
			y = self.score_images[0].buf.h//2
			for digit in score_string:
				digit = int(digit)
				self.buf = self.score_images[digit].buf
				super().add_to_frame(background, x, y)
				x += -self.gap + self.score_images[0].buf.w

		if cur_time >= self.freeze:
			add_up = max(7.27, (self.score - self.showscore)/12.72)
			if self.showscore + add_up > self.score:
				self.showscore = min(self.score, max(self.score - 1, self.showscore + 0.05))
			else:
				self.showscore += add_up

