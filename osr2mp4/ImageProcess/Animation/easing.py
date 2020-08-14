def easingout(time, initial, change, duration):
	t = time / duration
	return -change * t * (t - 2) + initial
