import math


def diste(pos1, pos2):
	return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def next_t(curve, prev_t, distance, cur_dist, going_forward, precise=False):
	"""
	Slider should have the same speed but right now with the current Bezier at() method it doesn't have the same speed bezier(0)-bezier(0.1) and bezier(0.5-0.6)
	:param curve: list of position
	:param prev_t:
	:param distance: expected distance
	:param cur_dist: current distance
	:param going_forward:
	:param debug:
	:param precise:
	:return: t for bezier(t), new distance
	"""
	sign = -1
	if going_forward:
		sign = 1
	prev_t = round(prev_t * (len(curve)-1))
	i = prev_t
	prev_dist, prev_i = cur_dist, i
	while (cur_dist - distance) * sign < 0:
		prev_i = i
		prev_dist = cur_dist
		i += 1 * sign
		if i >= len(curve):
			i -= 1
			break
		if i < 0:
			i = 0
			break
		cur_dist += diste(curve[prev_t], curve[i]) * sign
		prev_t = i

	if precise:
		pass
	# cur_dist = prev_dist
	# i = prev_i
	# if (cur_dist - distance) * sign > 0:
	# 	print(cur_dist, distance, going_forward)

	return i/(len(curve)-1), cur_dist
