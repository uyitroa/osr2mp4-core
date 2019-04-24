import numpy as np
import cv2
from curve import *


def convert(string):
	string = string.split(",")
	p_start = Position(int(string[0]), int(string[1]))

	slider_path = string[5]
	slider_path = slider_path.split("|")
	slider_path = slider_path[1:]

	ps = [p_start]
	for pos in slider_path:
		pos = pos.split(":")
		ps.append(Position(int(pos[0]), int(pos[1])))
		end_point = [int(pos[0]), int(pos[1])]

	pixel_length = float(string[7])
	return ps, pixel_length, end_point


def get_pos_from_bezier(test):
	cur_pos = test(0)
	t = 0.05
	curve_pos = [[int(cur_pos.x), int(cur_pos.y)]]
	min_x, max_x, min_y, max_y = float('inf'), 0, float('inf'), 0
	while t <= 1:
		cur_pos = test.at(t)
		curve_pos.append([int(cur_pos[0][0]), int(cur_pos[0][1])])
		t += 0.05
		min_x = min(min_x, int(cur_pos[0][0]))
		max_x = max(max_x, int(cur_pos[0][0]))

		min_y = min(min_y, int(cur_pos[0][1]))
		max_y = max(max_y, int(cur_pos[0][1]))
	width = max_x - min_x + thiccness * 2
	height = max_y - min_y + thiccness * 2
	return curve_pos, min_x, min_y, width, height


def draw(slider_border, slider_track, slider_override, curve_pos, img, radius):
	cv2.polylines(img, [curve_pos], 0, (*slider_border, 255), int(radius*2), 8)
	cv2.polylines(img, [curve_pos], 0, (*slider_track, 255), int(radius*2 - 10), 8)
	radius_sqrt = math.sqrt(radius)
	for c in range(5, int(radius), 2):
		# coefficient_color = ((3.5 * c + 12.5) * 64/radius) / 255
		# alpha = (4.5 * c + 32.5) * 64/radius
		coefficient_color = (radius_sqrt - math.sqrt(abs(radius - c))) / radius_sqrt
		print(coefficient_color)
		#coefficient_color = 1/(radius + 1 - c)
		#coefficient_color = c/(radius*0.9)
		cur_sliderride = slider_override * coefficient_color + np.array(slider_track)
		cur_sliderride[cur_sliderride > 255] = 255
		cv2.polylines(img, [curve_pos], 0, (*cur_sliderride, 255), int(radius*2 - c*2), 8)


WIDTH = 1920
HEIGHT = 1080
playfield_width, playfield_height = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8
scale = playfield_width/512

# circle = cv2.imread("underslider.png", -1)
# circle[:, :, 0:3] = [0, 0, 0]
slider_code = "88,100,0,2,0,B|158:2|424:158|140:382|88:100,1,475"
thiccness = 5
ps, length, end_point = convert(slider_code)
test = Bezier(ps, length)
curve_pos, min_x, min_y, width, height = get_pos_from_bezier(test)
# prepare_circle(img, [0, 0, 0], [255, 255, 255])
# draw(min_x, min_y, width, height, img, curve_pos)
curve_pos = np.array(curve_pos, np.int32)

img = np.zeros((384, 512, 4))
draw((0, 69, 255), (120, 60, 0), np.array([50, 50, 50]), curve_pos, img, 36.48)
# cv2.polylines(img, [curve_pos], 0, (255, 255, 255, 255), 60, 4)
# cv2.polylines(img, [curve_pos], 0, (0, 0, 0, 255), 50, 4)
# cv2.polylines(img, [curve_pos], 0, (5, 5, 5, 255), 45, 4)
# cv2.polylines(img, [curve_pos], 0, (15, 15, 15, 255), 40, 4)
# cv2.polylines(img, [curve_pos], 0, (25, 25, 25, 255), 30, 4)
# cv2.polylines(img, [curve_pos], 0, (40, 40, 40, 255), 15, 4)
# cv2.polylines(img, [curve_pos], 0, (45, 45, 45, 255), 13, 4)
# cv2.polylines(img, [curve_pos], 0, (50, 50, 50, 255), 10, 4)
# cv2.polylines(img, [curve_pos], 0, (0, 0, 0, 255), 1, 4)
cv2.imwrite("test.png", img)
