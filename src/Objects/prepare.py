import numpy as np
import ray
import cv2


class Ressources():
	def __init__(self, maxcolors, circle_frames, slidercircle_frames, orig_img, overlay, radius_scale, img,
	             number_drawer, gap, slider_combo, approachCircle, opacity_interval, overlay_filename, orig_cols, orig_rows, default_circle_size, cs, colors, slider_circle, maxcombo):
		self.maxcombo = maxcombo
		self.slider_circle = slider_circle
		self.colors = colors
		self.overlay_filename = overlay_filename
		self.orig_cols = orig_cols
		self.orig_rows = orig_rows
		self.default_circle_size = default_circle_size
		self.cs = cs
		self.overlay = overlay
		self.radius_scale = radius_scale
		self.img = img
		self.number_drawer = number_drawer
		self.gap = gap
		self.slider_combo = slider_combo
		self.approachCircle = approachCircle
		self.opacity_interval = opacity_interval
		self.orig_img = orig_img
		self.maxcolors = maxcolors
		self.circle_frames = circle_frames
		self.slidercircle_frames = slidercircle_frames


def add_color(self, image, color):
	red = color[0] / 255.0
	green = color[1] / 255.0
	blue = color[2] / 255.0
	image[:, :, 0] = np.multiply(image[:, :, 0], blue, casting='unsafe')
	image[:, :, 1] = np.multiply(image[:, :, 1], green, casting='unsafe')
	image[:, :, 2] = np.multiply(image[:, :, 2], red, casting='unsafe')
	image[image > 255] = 255


def overlayhitcircle(self, background, x_offset, y_offset, overlay_image):
	# still ned 4 channels so cannot do to_3channel before.
	y1, y2 = y_offset - int(overlay_image.shape[0] / 2), y_offset + int(overlay_image.shape[0] / 2)
	x1, x2 = x_offset - int(overlay_image.shape[1] / 2), x_offset + int(overlay_image.shape[1] / 2)

	y1, y2, ystart, yend = checkOverdisplay(self, y1, y2, background.shape[0])
	x1, x2, xstart, xend = checkOverdisplay(self, x1, x2, background.shape[1])

	alpha_s = overlay_image[ystart:yend, xstart:xend, 3] / 255.0
	alpha_l = 1 - alpha_s
	for c in range(4):
		background[y1:y2, x1:x2, c] = overlay_image[ystart:yend, xstart:xend, c] * alpha_s + \
		                              alpha_l * background[y1:y2, x1:x2, c]


def overlay_approach(self, background, x_offset, y_offset, circle_img):
	# still ned 4 channels so cannot do to_3channel before.
	y1, y2 = y_offset - int(circle_img.shape[0] / 2), y_offset + int(circle_img.shape[0] / 2)
	x1, x2 = x_offset - int(circle_img.shape[1] / 2), x_offset + int(circle_img.shape[1] / 2)

	y1, y2, ystart, yend = checkOverdisplay(self, y1, y2, background.shape[0])
	x1, x2, xstart, xend = checkOverdisplay(self, x1, x2, background.shape[1])

	alpha_s = background[y1:y2, x1:x2, 3] / 255.0
	alpha_l = 1 - alpha_s
	for c in range(4):
		background[y1:y2, x1:x2, c] = circle_img[ystart:yend, xstart:xend, c] * alpha_l + \
		                              alpha_s * background[y1:y2, x1:x2, c]


# crop everything that goes outside the screen
def checkOverdisplay(self, pos1, pos2, limit):
	start = 0
	end = pos2 - pos1
	if pos1 >= limit:
		return 0, 0, 0, 0
	if pos2 <= 0:
		return 0, 0, 0, 0

	if pos1 < 0:
		start = -pos1
		pos1 = 0
	if pos2 >= limit:
		end -= pos2 - limit
		pos2 = limit
	return pos1, pos2, start, end


def change_size(self, new_row, new_col, inter_type=cv2.INTER_AREA):
	n_rows = int(new_row * self.orig_rows)
	n_rows -= int(n_rows % 2 == 1)  # need to be even
	n_cols = int(new_col * self.orig_cols)
	n_cols -= int(n_cols % 2 == 1)  # need to be even
	self.img = cv2.resize(self.orig_img, (n_cols, n_rows), interpolation=inter_type)



def to_3channel(self, image):
	# convert 4 channel to 3 channel, so we can ignore alpha channel, this will optimize the time of add_to_frame
	# where we needed to do each time alpha_s * img[:, :, 0:3]. Now we don't need to do it anymore
	alpha_s = image[:, :, 3] / 255.0
	for c in range(3):
		image[:, :, c] = (image[:, :, c] * alpha_s).astype(self.orig_img.dtype)


def prepare_circle(self):
	circles_id = []
	sliders_id = []
	for x in range(1, self.maxcolors + 1):
		id1, id2 = _prepare_circle.remote(self, x)
		circles_id.append(id1)
		sliders_id.append(id2)
	print("here done")

	for x in range(1, self.maxcolors + 1):
		self.circle_frames[x] = ray.get(circles_id)
		self.slidercircle_frames[x] = ray.get(sliders_id)


@ray.remote(num_return_vals=2)
def _prepare_circle(self, c):
	# prepare every single frame before entering the big loop, this will save us a ton of time since we don't need
	# to overlap number, circle overlay and approach circle every single time.
	circle_frames = []
	slidercircle_frames = []
	color = self.colors["Combo" + str(c)]

	orig_color_img = np.copy(self.orig_img)
	add_color(self, orig_color_img, color)
	cv2.imwrite(str(c) + "test.png", orig_color_img)
	overlayhitcircle(self, orig_color_img, int(self.overlay.orig_cols / 2), int(self.overlay.orig_rows / 2),
	                 self.overlay.img)
	tmp = self.orig_img
	self.orig_img = orig_color_img
	change_size(self, self.radius_scale * 1.13, self.radius_scale * 1.13, inter_type=cv2.INTER_LINEAR)
	orig_color_img = np.copy(self.img)
	self.orig_img = tmp
	circle_frames.append([])

	orig_color_slider = np.copy(self.slider_circle.orig_img)
	add_color(self, orig_color_slider, color)
	self.slider_circle.img = np.copy(orig_color_slider)
	slidercircle_frames.append({})  # so to find the right combo will be faster

	for x in range(1, self.maxcombo[c] + 1):
		self.number_drawer.draw(self.img, x, self.gap)

		if x in self.slider_combo:
			self.number_drawer.draw(self.slider_circle.img, x, self.gap)
			slidercircle_frames[-1][x] = []
		alpha = 0
		circle_frames[-1].append([])
		for i in range(len(self.approachCircle.approach_frames)):
			approach_circle = np.copy(self.approachCircle.approach_frames[i])

			x_offset = int(approach_circle.shape[1] / 2)
			y_offset = int(approach_circle.shape[0] / 2)

			if x in self.slider_combo:
				approach_slider = np.copy(approach_circle)
				overlay_approach(self, approach_slider, x_offset, y_offset, self.slider_circle.img)
				approach_slider[:, :, 3] = approach_slider[:, :, 3] * (alpha / 100)
				to_3channel(self, approach_slider)
				slidercircle_frames[-1][x].append(approach_slider)

			overlay_approach(self, approach_circle, x_offset, y_offset, self.img)
			approach_circle[:, :, 3] = approach_circle[:, :, 3] * (alpha / 100)
			to_3channel(self, approach_circle)

			circle_frames[-1][-1].append(approach_circle)
			alpha = min(100, alpha + self.opacity_interval)

		self.img = np.copy(orig_color_img)
		self.slider_circle.img = np.copy(orig_color_slider)
	print("done", c)
	return circle_frames, slidercircle_frames


def _main(maxcolors, circle_frames, slidercircle_frames, orig_img, overlay, radius_scale, img, number_drawer, gap,
          slider_combo, approachCircle, opacity_interval, overlay_filename, orig_cols, orig_rows, default_circle_size, cs, colors, slider_circle, maxcombo):
	self = Ressources(maxcolors, circle_frames, slidercircle_frames, orig_img, overlay, radius_scale, img,
	                  number_drawer, gap, slider_combo, approachCircle, opacity_interval, overlay_filename, orig_cols, orig_rows, default_circle_size, cs, colors, slider_circle, maxcombo)
	prepare_circle(self)