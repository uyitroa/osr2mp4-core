import cv2
from Curves.curve import *


class GenerateSlider:
	def __init__(self, sliderborder, slideroverride, radius, scale):
		"""
		:param sliderborder: list, color of the slider's border
		:param slideroverride: list, color of the slider's body
		:param radius: float, size of slider
		:param scale: float, current resolution with 512x384
		"""
		self.sliderborder = sliderborder
		self.sliderborder[0], self.sliderborder[2] = self.sliderborder[2], self.sliderborder[0]
		self.sliderborder = tuple(self.sliderborder)

		self.slideroverride = slideroverride
		self.slideroverride[0], self.slideroverride[2] = self.slideroverride[2], self.slideroverride[0]
		self.slideroverride = tuple(self.slideroverride)

		self.radius = radius
		self.scale = scale

	def convert(self, slider_code):
		string = slider_code.split(",")
		ps = [Position(int(string[0]) * self.scale, int(string[1]) * self.scale)]
		slider_path = string[5]
		slider_path = slider_path.split("|")
		slider_type = slider_path[0]
		slider_path = slider_path[1:]

		for pos in slider_path:
			pos = pos.split(":")
			ps.append(Position(int(pos[0]) * self.scale, int(pos[1]) * self.scale))

		pixel_length = float(string[7])
		return ps, pixel_length * self.scale, slider_type

	def get_pos_from_class(self, baiser_class):
		# get pos from t = 0 to t = 1
		cur_pos = baiser_class(0)
		t = 0.02
		curve_pos = [[int(cur_pos.x), int(cur_pos.y)]]
		while t <= 1:
			cur_pos = baiser_class(t)
			curve_pos.append([int(cur_pos.x), int(cur_pos.y)])
			t += 0.02
		return curve_pos

	def get_min_max(self, curve_pos):
		# get pos where slider start drawing and end drawing, basically reduce image size without touching the slider
		min_x, min_y, max_x, max_y = curve_pos[0][0], curve_pos[0][1], curve_pos[0][0], curve_pos[0][1]
		for index in range(0, len(curve_pos)):
			min_x = min(min_x, curve_pos[index][0])
			min_y = min(min_y, curve_pos[index][1])

			max_x = max(max_x, curve_pos[index][0])
			max_y = max(max_y, curve_pos[index][1])

		return min_x, min_y, max_x, max_y

	def draw(self, curve_pos):
		to_color = np.array([50, 50, 50])  # slider gradually become this color, the closer to the center the closer the color
		im = np.zeros((math.ceil(384 * self.scale), math.ceil(512 * self.scale), 4))
		curve_pos = np.array(curve_pos)

		cv2.polylines(im, [curve_pos], False, (*self.sliderborder, 255), int(self.radius*2*self.scale), cv2.LINE_AA)
		cv2.polylines(im, [curve_pos], False, (*self.slideroverride, 255), int((self.radius-8)*2*self.scale), cv2.LINE_AA)

		# make shadow color effect
		for c in range(4, int(self.radius), 2):
			coefficient = c / self.radius
			cur_slider = to_color * coefficient + np.array(self.slideroverride)
			cur_slider[cur_slider > 255] = 255
			cur_slider = tuple(cur_slider)

			cv2.polylines(im, [curve_pos], False, (*cur_slider, 255), int((self.radius*2 - c*2) * self.scale), cv2.LINE_AA)
		return im

	def get_slider_img(self, slider_code):
		ps, pixel_length, slider_type = self.convert(slider_code)
		baiser = Curve.from_kind_and_points(slider_type, ps, pixel_length)  # get the right curve class
		curve_pos = self.get_pos_from_class(baiser)

		min_x, min_y, max_x, max_y = self.get_min_max(curve_pos)  # start y end y start x end x
		img = self.draw(curve_pos)

		# crop useless part of image
		extended = math.sqrt(2 * ((self.radius * self.scale) ** 2))
		left_y_corner = int(min_y - extended) if int(min_y - extended) >= 0 else 0
		left_x_corner = int(min_x - extended) if int(min_x - extended) >= 0 else 0
		right_y_corner = math.ceil(max_y + extended) if math.ceil(max_y + extended) < img.shape[0] else img.shape[0]
		right_x_corner = math.ceil(max_x + extended) if math.ceil(max_x + extended) < img.shape[1] else img.shape[1]

		img = img[left_y_corner:right_y_corner, left_x_corner:right_x_corner]

		# drew the slider at high res first, then scale down to get smoother slider
		img = cv2.resize(img, (int(img.shape[1] / self.scale), int(img.shape[0] / self.scale)), interpolation=cv2.INTER_AREA)
		img = cv2.blur(img, (5, 5))  # blur to smooth out the slider
		return img


if __name__ == "__main__":
	# slidercode = "96,180,0,2,0,B|286:44|286:44|416:201|416:201|251:340|251:340|95:179|95:179,1,875"
	# slidercode = "130,77,0,2,0,B|414:155|98:307,1,375"
	# slidercode = "105,194,0,2,0,L|407:190,1,300"
	# slidercode = "226,81,0,2,0,B|427:107|272:303|85:222|226:81,1,400"
	# slidercode = "142,314,0,2,0,B|267:54|267:54|387:330|387:330|95:128|95:128|417:124|417:124|141:314,1,1600"
	# slidercode = "182,326,3923,2,0,P|99:174|394:243,1,700"
	slidercode = "485,360,99863,2,0,P|483:342|470:225,1,135.8307"
	WIDTH = 1920
	HEIGHT = 1080
	playfield_width, playfield_height = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8
	scale = playfield_width/512
	gs = GenerateSlider([255, 69, 0], [0, 60, 120], 36.48, scale)
	cv2.imwrite("test.png", gs.get_slider_img(slidercode))