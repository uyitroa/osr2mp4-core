import numpy as np
from PIL import Image
import cv2
import aggdraw
from curve import *


class GenerateSlider:
	def __init__(self, sliderborder, slideroverride, radius):
		self.sliderborder = sliderborder
		self.sliderborder[0], self.sliderborder[2] = self.sliderborder[2], self.sliderborder[0]
		self.sliderborder = tuple(self.sliderborder)

		self.slideroverride = slideroverride
		self.slideroverride[0], self.slideroverride[2] = self.slideroverride[2], self.slideroverride[0]
		self.slideroverride = tuple(self.slideroverride)

		self.radius = radius

	def convert(self, slider_code):
		string = slider_code.split(",")
		ps = [Position(int(string[0]), int(string[1]))]
		slider_path = string[5]
		slider_path = slider_path.split("|")
		slider_path = slider_path[1:]

		for pos in slider_path:
			pos = pos.split(":")
			ps.append(Position(int(pos[0]), int(pos[1])))

		pixel_length = float(string[7])
		return ps, pixel_length

	def get_pos_from_bezier(self, baiser_class):
		cur_pos = baiser_class(0)
		t = 0.02
		curve_pos = [int(cur_pos.x), int(cur_pos.y)]
		while t <= 1:
			cur_pos = baiser_class.at(t)
			curve_pos.append(int(cur_pos[0][0]))
			curve_pos.append(int(cur_pos[0][1]))
			t += 0.02
		return curve_pos

	def get_min_max(self, curve_pos):
		min_x, min_y, max_x, max_y = curve_pos[0], curve_pos[1], curve_pos[0], curve_pos[1]
		for index in range(0, len(curve_pos), 2):
			min_x = min(min_x, curve_pos[index])
			min_y = min(min_y, curve_pos[index + 1])

			max_x = max(max_x, curve_pos[index])
			max_y = max(max_y, curve_pos[index + 1])

		return min_x, min_y, max_x, max_y

	def get_pos(self, x1, y1, radius):
		x_border1 = x1 - radius
		y_border1 = y1 - radius
		x_border2 = x1 + radius
		y_border2 = y1 + radius

		return x_border1, y_border1, x_border2, y_border2

	def draw(self, curve_pos):
		to_color = np.array([50, 50, 50])
		im = Image.new('RGBA', (512, 384), (0, 0, 0, 0))
		draw = aggdraw.Draw(im)
		draw.setantialias(True)

		xstart1, ystart1, xstart2, ystart2 = self.get_pos(curve_pos[0], curve_pos[1], self.radius)
		xend1, yend1, xend2, yend2 = self.get_pos(curve_pos[-2], curve_pos[-1], self.radius)
		draw.ellipse((xstart1, ystart1, xstart2, ystart2), None, aggdraw.Brush(self.sliderborder))
		draw.ellipse((xend1, yend1, xend2, yend2), None, aggdraw.Brush(self.sliderborder))

		draw.line(curve_pos, aggdraw.Pen(self.sliderborder, int(self.radius) * 2))
		draw.line(curve_pos, aggdraw.Pen(self.slideroverride, int(self.radius - 8) * 2))
		for c in range(4, int(self.radius), 2):
			coefficient = c / self.radius
			cur_slider = to_color * coefficient + np.array(self.slideroverride)
			cur_slider[cur_slider > 255] = 255
			cur_slider = cur_slider.astype(int)
			cur_slider = tuple(cur_slider)
			draw.ellipse((xstart1 + c, ystart1 + c, xstart2 - c, ystart2 - c), None, aggdraw.Brush(cur_slider))
			draw.ellipse((xend1 + c, yend1 + c, xend2 - c, yend2 - c), None, aggdraw.Brush(cur_slider))
			draw.line(curve_pos, aggdraw.Pen(cur_slider, int(self.radius * 2 - c * 2)))
		draw.flush()
		return im

	def get_slider_img(self, slider_code):
		ps, pixel_length = self.convert(slider_code)
		baiser = Bezier(ps, pixel_length)
		curve_pos = self.get_pos_from_bezier(baiser)
		min_x, min_y, max_x, max_y = self.get_min_max(curve_pos)
		im = self.draw(curve_pos)
		img = np.array(im)
		img = img[int(min_y - self.radius):math.ceil(max_y + self.radius),
		      int(min_x - self.radius):math.ceil(max_x + self.radius)]
		return img


if __name__ == "__main__":
	slidercode = "150,131,0,2,0,B|362:78|338:306|172:295,1,375"
	gs = GenerateSlider([255, 69, 0], [0, 60, 120], 36.48)
	cv2.imwrite("test.png", gs.get_slider_img(slidercode))