from math import sqrt


def easingout(time, initial, change, duration):
	t = time / duration
	return -change * t * (t - 2) + initial


def easingoutcubic(time, initial, change, duration):
	t = time/duration - 1
	return change * (t * t * t + 1) + initial


def easingoutquint(time, initial, change, duration):
	t = time/duration - 1
	return change * (t * t * t * t * t + 1) + initial


def easingoutcirc(time, initial, change, duration):
	t = time / duration - 1
	return change * sqrt(1 - t * t) + initial
