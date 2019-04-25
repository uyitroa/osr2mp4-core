import math
import numpy as np
from PIL import Image
import cv2
import aggdraw
from curve import *


def convert(string):
	string = string.split(",")
	ps = [Position(int(string[0]), int(string[1]))]
	slider_path = string[5]
	slider_path = slider_path.split("|")
	slider_path = slider_path[1:]

	for pos in slider_path:
		pos = pos.split(":")
		ps.append(Position(int(pos[0]), int(pos[1])))

		end_point = [int(pos[0]), int(pos[1])]

	pixel_length = float(string[7])
	return ps, pixel_length#, end_point


def get_pos_from_bezier(test):
	cur_pos = test(0)
	t = 0.02
	curve_pos = [int(cur_pos.x), int(cur_pos.y)]
	while t <= 1:
		cur_pos = test.at(t)
		curve_pos.append(int(cur_pos[0][0]))
		curve_pos.append(int(cur_pos[0][1]))
		t += 0.02

	return curve_pos


def draw(sliderborder, slideroverride, radius, curve_pos):
	to_color = np.array([50, 50, 50])
	im = Image.new('RGBA', (512, 384), (0, 0, 0, 0))
	draw = aggdraw.Draw(im)
	draw.setantialias(True)
	draw.line(curve_pos, aggdraw.Pen(sliderborder, int(radius) * 2))
	draw.line(curve_pos, aggdraw.Pen(slideroverride, int(radius - 8) * 2))
	for c in range(4, int(radius), 2):
		coefficient = c/radius
		cur_slider = to_color * coefficient + np.array(slideroverride)
		cur_slider[cur_slider > 255] = 255
		cur_slider = cur_slider.astype(int)
		cur_slider = tuple(cur_slider)
		draw.line(curve_pos, aggdraw.Pen(cur_slider, int(radius*2 - c*2)))
	draw.flush()
	return im

# for x in range(1000):
code = "88,100,0,2,0,B|158:2|424:158|140:382|88:100,1,475"
ps, pixel_length = convert(code)
test = Bezier(ps, pixel_length)
curve_pos = get_pos_from_bezier(test)
color = [255, 69, 0]
color[0], color[2] = color[2], color[0]
color = tuple(color)

override = [0, 60, 120]
override[0], override[2] = override[2], override[0]
override = tuple(override)
im = draw(color, override, 36.48, curve_pos)
img = np.array(im)
cv2.imwrite("test.png", img)
