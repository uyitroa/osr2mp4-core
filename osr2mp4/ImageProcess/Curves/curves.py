import math

import cv2

from .adjustcurve import next_t, diste
import numpy as np
from . import constants, mathhelper
from .curve2 import LinearB, PerfectB, Curve


class ASlider:
	def __init__(self, points, pixel_length):
		self.points = points
		self.pixel_length = pixel_length
		self.cur_t = 0
		self.cur_dist = 0

	def update(self, t, dist):
		pass

	def clear(self):
		self.cur_t = 0
		self.cur_dist = 0


class Linear(ASlider):  # Because it made sense at the time...
	def __init__(self, points, pixel_length):
		super().__init__(points, pixel_length)
		self.calc_points()

	def calc_points(self):
		self.pos = [self.points[0]]
		l = LinearB(self.points, self.pixel_length)
		endpos = l(1)
		self.pos.append([endpos.x, endpos.y])

	def at(self, dist, forward, alone=None):
		t = dist/self.pixel_length
		sum_x = (1 - t) * self.pos[0][0] + t * self.pos[-1][0]
		sum_y = (1 - t) * self.pos[0][1] + t * self.pos[-1][1]
		return [sum_x, sum_y], t


class Bezier(ASlider):
	def __init__(self, points, pixel_length):
		super().__init__(points, pixel_length)
		self.order = len(self.points)
		self.pos = []

		self.pos_prev = None
		self.dist_cur = 0
		self.endslicedraw = None
		self.calc_points()

	def calc_points(self):
		if len(self.pos) != 0:  # This should never happen but since im working on this I want to warn myself if I fuck up
			raise Exception("Bezier was calculated twice!")

		sub_points = []
		for i in range(len(self.points)):
			if i == len(self.points) - 1:
				sub_points.append(self.points[i])
				self.bezier(sub_points)
				sub_points.clear()
			elif len(sub_points) > 1 and self.points[i] == sub_points[-1]:
				self.bezier(sub_points)
				sub_points.clear()

			sub_points.append(self.points[i])

	def bezier(self, points):
		order = len(points)
		step = 0.25/constants.SLIDER_QUALITY/order  # Normaly 0.0025
		i = 0
		n = order - 1
		reachend = False
		while i < 1 + step:
			# if reachend:
			# 	break
			# if i >= 1:
			# 	i = 1
			# 	reachend = True
			x = 0
			y = 0
			for p in range(n + 1):
				a = mathhelper.cpn(p, n) * pow((1 - i), (n - p)) * pow(i, p)
				x += a * points[p][0]
				y += a * points[p][1]

			point = [x, y]

			if self.pos_prev is not None:
				self.dist_cur += diste(self.pos_prev, point)
			self.pos_prev = point
			if self.dist_cur > self.pixel_length:
				break
			self.pos.append(point)
			i += step

	def at(self, dist, forward, alone=None):
		if forward is None:
			t = dist/self.pixel_length
			return self.pos[int(t * (len(self.pos)-1))], t

		if alone:
			t, cur_dst = next_t(self.pos, int(not forward), dist, int(not forward) * self.pixel_length, forward)
			i = round(t * (len(self.pos) - 1))
			return self.pos[i], t

		t, cur_dst = next_t(self.pos, self.cur_t, dist, self.cur_dist, forward)
		i = round(t * (len(self.pos) - 1))
		self.update(t, cur_dst)

		return self.pos[i], t

	def update(self, t, dist):
		self.cur_t = t
		self.cur_dist = dist


class Catmull(ASlider):  # Yes... I cry deep down on the inside aswell
	def __init__(self, points, pixel_length):
		super().__init__(points, pixel_length)
		self.order = len(points)
		self.step = 0.25 / constants.SLIDER_QUALITY  # Normaly 0.025
		self.pos = []
		self.calc_points()

	def calc_points(self):
		if len(
				self.pos) != 0:  # This should never happen but since im working on this I want to warn myself if I fuck up
			raise Exception("Catmull was calculated twice!")

		for x in range(self.order - 1):
			t = 0
			while t < self.step + 1:
				if x >= 1:
					v1 = self.points[x - 1]
				else:
					v1 = self.points[x]

				v2 = self.points[x]

				if x + 1 < self.order:
					v3 = self.points[x + 1]
				else:
					v3 = calc(v2, 1, calc(v2, -1, v1))

				if x + 2 < self.order:
					v4 = self.points[x + 2]
				else:
					v4 = calc(v3, 1, calc(v3, -1, v2))

				point = get_point([v1, v2, v3, v4], t)
				self.pos.append(point)
				t += self.step

	def at(self, dist, forward, alone=False):
		# return {
		# 	0: False,
		# 	1: self.points[0],
		# }.get(self.order, self.rec(dist))
		return self.rec(dist), dist/self.pixel_length

	def rec(self, length):
		return mathhelper.point_at_distance(self.pos, length)


class Perfect(ASlider):
	def __init__(self, points, pixel_length):
		super().__init__(points, pixel_length)
		self.pos = []
		self.c = Curve.from_kind_and_points("P", self.points, self.pixel_length)
		self.setup_path()

	def setup_path(self):
		tol = 1 / max(1, self.pixel_length / 650)
		tol = 0.025 * tol
		t = 0
		while t <= 1:
			pos = self.c(t)
			self.pos.append([pos.x, pos.y])
			t += tol

	def at(self, dist, forward, alone=None):
		t = dist/self.pixel_length
		pos = self.c(t)
		return [pos.x, pos.y], t


def get_point(p, length):
	x = mathhelper.catmull([o[0] for o in p], length)
	y = mathhelper.catmull([o[1] for o in p], length)
	return [x, y]


def get_circum_circle(p):
	d = 2 * (p[0][0] * (p[1][1] - p[2][1]) + p[1][0] * (p[2][1] - p[0][1]) + p[2][0] * (p[0][1] - p[1][1]))

	if d == 0:
		raise Exception("Invalid circle! Unable to chose angle.")

	ux = ((pow(p[0][0], 2) + pow(p[0][1], 2)) * (p[1][1] - p[2][1]) + (pow(p[1][0], 2) + pow(p[1][1], 2)) * (
				p[2][1] - p[0][1]) + (pow(p[2][0], 2) + pow(p[2][1], 2)) * (p[0][1] - p[1][1])) / d
	uy = ((pow(p[0][0], 2) + pow(p[0][1], 2)) * (p[2][0] - p[1][0]) + (pow(p[1][0], 2) + pow(p[1][1], 2)) * (
				p[0][0] - p[2][0]) + (pow(p[2][0], 2) + pow(p[2][1], 2)) * (p[1][0] - p[0][0])) / d

	px = ux - p[0][0]
	py = uy - p[0][1]
	r = pow(pow(px, 2) + pow(py, 2), 0.5)

	return ux, uy, r


def is_left(p):
	return ((p[1][0] - p[0][0]) * (p[2][1] - p[0][1]) - (p[1][1] - p[0][1]) * (p[2][0] - p[0][0])) < 0


def rotate(cx, cy, p, radians):
	cos = math.cos(radians)
	sin = math.sin(radians)

	x = (cos * (p[0] - cx)) - (sin * (p[1] - cy)) + cx
	y = (sin * (p[0] - cx)) + (cos * (p[1] - cy)) + cy

	return [x, y]


def calc(p, value, other):
	x = p[0] + value * other[0]
	y = p[1] + value * other[1]
	return [x, y]

def getclass(slidertype, points, pixellength):
	if slidertype == "L":
		return Linear(points, pixellength)
	if slidertype == "B":
		return Bezier(points, pixellength)
	if slidertype == "P":
		return Perfect(points, pixellength)
	if slidertype == "C":
		return Catmull(points, pixellength)
	return None


if __name__ == "__main__":
	slidercode = "371,98,261846,6,0,B|441:100|493:117|545:83|537:10|480:-28|406:-4|393:39|424:90|453:165|453:165|488:161|517:145|517:145|536:176|526:210|526:210|485:236|410:230|410:230|454:275|454:275|417:296|417:296|441:327|441:327|398:363|398:363|325:375|268:317|185:336|185:336|179:261|289:320|289:320,1,1200.00004577637,6|0,0:0|0:0,0:0:0:0:"
	# slidercode = "5,256,435300,6,0,B|9:201|55:179|55:179|119:191|125:283,2,225.000008583069,6|4|4,0:0|0:0|0:0,0:0:0:0:"
	# slidercode = "324,308,173481,6,0,B|384:328|460:308|484:228|484:228|464:272|420:280|420:280|360:268|320:192|428:136|388:84|360:40|304:32|268:40|232:68|228:108|240:132|264:148|284:148|304:136,1,700,2|2,0:0|0:0,0:0:0:0:"
	WIDTH = 1920
	HEIGHT = 1080
	playfield_width, playfield_height = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8
	scale = playfield_width/512
	gs = GenerateSlider([255, 69, 0], [0, 60, 120], 36.48, 2)
	ps, length, stype = gs.convert_string(slidercode)
	# ps = gs.convert(ps)
	# b = Bezier(ps)
	for x in range(10):
		b = Bezier(ps)
	img, x, y, curvepos = gs.get_slider_img(stype, np.int32(b.pos), length)
	square = np.full((2, 2, 4), 255)
	img[y-1:y+1, x-1:x+1] = square
	cv2.imwrite("asdf.png", img)
