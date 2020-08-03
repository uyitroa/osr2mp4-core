from libcpp.vector cimport vector

cdef extern from "curves.h":
	vector[vector[float]] get_bezier(vector[vector[float]] controlpoints)
	vector[vector[float]] get_catmull(vector[vector[float]] controlpoints)
	vector[vector[float]] get_linear(vector[vector[float]] controlpoints)
	vector[vector[float]] get_perfect(vector[vector[float]] controlpoints)
	vector[double] adjust_curve(vector[vector[float]] path, double expected_length)
	vector[float] position_at(vector[vector[float]]path, vector[double] cum_length, double length)

def create_curve(curve_type, control_points, expected_length):
	cdef vector[vector[float]] cp = control_points
	cdef vector[vector[float]] path
	if curve_type == "B":
		path = get_bezier(control_points)
	if curve_type == "L":
		path = get_linear(control_points)
	if curve_type == "C":
		path = get_catmull(control_points)
	if curve_type == "P":
		path = get_perfect(control_points)
	cum_length = adjust_curve(path, expected_length)
	return path, cum_length

def binary_search(v, value):
	cdef int mid = 0
	cdef int left = 0
	cdef int right = len(v)

	while left < right:
		mid = left + (right - left)/2
		if value > v[mid]:
			left = mid+1
		elif value < v[mid]:
			right = mid
		else:
			break
	return right

def get_pos_at(path, cum_length, length):
	#cdef vector[vector[float]] cpath = path
	#cdef vector[double] ccum_length = cum_length
	#return position_at(cpath, ccum_length, length)
	if len(path) == 0 or len(cum_length) == 0:
		return [0, 0]
	if length == 0:
		return path[0]
	if length > cum_length[len(cum_length)-1]:
		return path[len(path)-1]

	cdef int i = binary_search(cum_length, length)

	if i > len(cum_length) - 1:
		i = len(cum_length) - 1

	cdef double length_next = cum_length[i]
	cdef double length_previous
	if i == 0:
		length_previous = 0
	else:
		length_previous = cum_length[i-1]

	i += 1

	res = [path[i-1][0], path[i-1][1]]
	
	p1 = path[i-1]
	p2 = path[i]

	if length_previous != length_next:
		res[0] = res[0] + (p2[0] - p1[0]) * (1 - (length_next - length) / (length_next - length_previous))
		res[1] = res[1] + (p2[1] - p1[1]) * (1 - (length_next - length) / (length_next - length_previous))

	return res


