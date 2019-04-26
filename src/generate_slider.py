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


def rotate_image(mat, angle):
	"""
	Rotates an image (angle in degrees) and expands image to avoid cropping
	"""

	height, width = mat.shape[:2] # image shape has 3 dimensions
	image_center = (width/2, height/2) # getRotationMatrix2D needs coordinates in reverse order (width, height) compared to shape

	rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1.)

	# rotation calculates the cos and sin, taking absolutes of those.
	abs_cos = abs(rotation_mat[0,0])
	abs_sin = abs(rotation_mat[0,1])

	# find the new width and height bounds
	bound_w = int(height * abs_sin + width * abs_cos)
	bound_h = int(height * abs_cos + width * abs_sin)

	# subtract old image center (bringing image back to origo) and adding the new image center coordinates
	rotation_mat[0, 2] += bound_w/2 - image_center[0]
	rotation_mat[1, 2] += bound_h/2 - image_center[1]

	# rotate image with the new bounds and translated rotation matrix
	rotated_mat = cv2.warpAffine(mat, rotation_mat, (bound_w, bound_h))
	return rotated_mat


def get_pos(x1, y1, radius):
	x_border1 = x1 - radius
	y_border1 = y1 - radius
	x_border2 = x1 + radius
	y_border2 = y1 + radius

	return x_border1, y_border1, x_border2, y_border2


def draw(sliderborder, slideroverride, radius, curve_pos):
	to_color = np.array([50, 50, 50])
	im = Image.new('RGBA', (512, 384), (0, 0, 0, 0))
	draw = aggdraw.Draw(im)
	draw.setantialias(True)

	xstart1, ystart1, xstart2, ystart2 = get_pos(curve_pos[0], curve_pos[1], radius)
	xend1, yend1, xend2, yend2 = get_pos(curve_pos[-2], curve_pos[-1], radius)
	draw.ellipse((xstart1, ystart1, xstart2, ystart2), None, aggdraw.Brush(sliderborder))
	draw.ellipse((xend1, yend1, xend2, yend2), None, aggdraw.Brush(sliderborder))

	draw.line(curve_pos, aggdraw.Pen(sliderborder, int(radius) * 2))
	draw.line(curve_pos, aggdraw.Pen(slideroverride, int(radius - 8) * 2))
	for c in range(4, int(radius), 2):
		coefficient = c/radius
		cur_slider = to_color * coefficient + np.array(slideroverride)
		cur_slider[cur_slider > 255] = 255
		cur_slider = cur_slider.astype(int)
		cur_slider = tuple(cur_slider)
		draw.ellipse((xstart1 + c, ystart1 + c, xstart2 - c, ystart2 - c), None, aggdraw.Brush(cur_slider))
		draw.ellipse((xend1 + c, yend1 + c, xend2 - c, yend2 - c), None, aggdraw.Brush(cur_slider))
		draw.line(curve_pos, aggdraw.Pen(cur_slider, int(radius*2 - c*2)))
	draw.flush()
	return im


# for x in range(1000):
code = "150,131,0,2,0,B|362:78|338:306|172:295,1,375"
ps, pixel_length = convert(code)
test = Bezier(ps, pixel_length)
curve_pos = get_pos_from_bezier(test)

color = [255, 69, 0]
color[0], color[2] = color[2], color[0]
color = tuple(color)
override = [0, 60, 120]
override[0], override[2] = override[2], override[0]
override = tuple(override)

circle = cv2.imread("dessous.png")
im = draw(color, override, 36.48, curve_pos)
img = np.array(im)
cv2.imwrite("test.png", img)
