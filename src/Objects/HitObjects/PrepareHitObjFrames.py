from Objects.abstracts import *

hitcircle = "hitcircle"
hitcircleoverlay = "hitcircleoverlay"
sliderstartcircleoverlay = "sliderstartcircleoverlay"
sliderstartcircle = "sliderstartcircle"
approachcircle = "approachcircle"
sliderb = "sliderb"
sliderfollowcircle = "sliderfollowcircle"
sliderscorepiont = "sliderscorepoint"
reversearrow = "reversearrow"
spinnercircle = "spinner-circle"
spinnerbackground = "spinner-background"
spinnerbottom = "spinner-bottom"
spinnerspin = "spinner-spin"
spinnermetre = "spinner-metre"
spinnerapproachcircle = "spinner-approachcircle"
spinnertop = "spinner-top"
default_size = 128


# Circle

class HitCircleNumber(Images):
	def __init__(self, filename, circle_radius, default_circle_size):
		Images.__init__(self, filename)
		self.scale = circle_radius * 2 / default_circle_size
		self.change_size(self.scale, self.scale)
		self.orig_img = self.img.copy()
		self.orig_rows = self.img.size[1]
		self.orig_cols = self.img.size[0]
	# self.to_3channel()


class Number:
	def __init__(self, radius, path, default_circle_size):
		self.combo_number = []
		for x in range(10):
			self.combo_number.append(HitCircleNumber(path + "default-" + str(x), radius, default_circle_size))

	def draw(self, circle, number, overlap):
		"""
		:param circle: array of image circle
		:param number: number
		:param gap: distance between two digits
		"""
		number = str(number)
		size = (self.combo_number[0].img.size[0] - overlap) * (len(number) - 1)
		x_pos = int((circle.size[0] / 2) - (size / 2))
		y_pos = int(circle.size[1] / 2)

		for digit in number:
			self.combo_number[int(digit)].add_to_frame(circle, x_pos, y_pos, 4)
			x_pos += -overlap + self.combo_number[int(digit)].img.size[0]


class ApproachCircle(ACircle):
	def __init__(self, filename, hitcircle_cols, hitcircle_rows, scale, time_preempt, interval):
		ACircle.__init__(self, filename, hitcircle_cols, hitcircle_rows)
		self.scale = scale
		self.time_preempt = round(time_preempt)
		self.interval = int(interval)
		self.approach_frames = []
		# self.to_3channel()
		self.prepare_sizes()

	def prepare_sizes(self):
		scale = 3.5
		for time_left in range(self.time_preempt, 0, -self.interval):
			scale -= 2.5 * self.interval / self.time_preempt
			p = super().change_size(scale * self.scale, scale * self.scale, img=self.img)
			print(scale * self.scale, p.size)
			self.approach_frames.append(p)

	# self.approach_frames[3].save("asdf.png")
	# self.approach_frames[6].save("asdf1.png")
	# self.approach_frames[10].save("asdf2.png")

	def add_to_frame(self, background, x_offset, y_offset, time_left):
		self.img = self.approach_frames[int((self.time_preempt - time_left) / self.interval)]
		super().add_to_frame(background, x_offset, y_offset)


class CircleOverlay(ACircle):
	def __init__(self, filename, hitcircle_cols, hitcircle_rows):
		ACircle.__init__(self, filename, hitcircle_cols, hitcircle_rows)


class SliderCircleOverlay(ACircle):
	def __init__(self, filename, hitcircle_cols, hitcircle_rows):
		ACircle.__init__(self, filename, hitcircle_cols, hitcircle_rows)


class CircleSlider(ACircle):
	def __init__(self, filename, hitcircle_cols, hitcircle_rows):
		ACircle.__init__(self, filename, hitcircle_cols, hitcircle_rows)


class PrepareCircles(Images):
	def __init__(self, beatmap, path, scale, skin):
		Images.__init__(self, path + hitcircle)
		self.overlay_filename = path + hitcircleoverlay
		self.slideroverlay_filename = path + sliderstartcircleoverlay
		self.diff = beatmap.diff
		self.interval = 1000 / 60  # ms between 2 frames
		self.overlay_scale = 1.05
		self.ar = self.diff["ApproachRate"]
		self.cs = (54.4 - 4.48 * self.diff["CircleSize"]) * scale

		self.calculate_ar()
		self.load_circle()

		self.maxcolors = skin.colours["ComboNumber"]
		self.colors = skin.colours
		self.maxcombo = beatmap.max_combo
		self.overlap = int(skin.fonts["HitCircleOverlap"])

		self.slider_combo = beatmap.slider_combo
		self.slider_circle = CircleSlider(path + sliderstartcircle, self.orig_cols, self.orig_rows)

		self.number_drawer = Number(self.cs * 0.9, path, default_size)
		self.approachCircle = ApproachCircle(path + approachcircle, self.orig_cols, self.orig_rows, self.radius_scale,
		                                     self.time_preempt, self.interval)

		# frames = [color][number][alpha]
		self.circle_frames = []
		self.slidercircle_frames = []
		self.circle_fadeout = [[], []]
		self.prepare_circle()

	def create_black_circle(self):
		# black support so that slider color won't affect hitcircleslider color cuz alpha when it begins to appear
		self.circle_supporter = super().add_color(self.orig_img, (0, 0, 0))
		self.circle_supporter = self.change_size(self.radius_scale, self.radius_scale, img=self.circle_supporter)
		self.circle_supporter.putalpha()

	def get_frames(self):
		return self.slidercircle_frames, self.circle_frames, self.circle_fadeout

	def calculate_ar(self):
		if self.ar < 5:
			self.time_preempt = 1200 + 600 * (5 - self.ar) / 5
			self.fade_in = 800 + 400 * (5 - self.ar) / 5
		elif self.ar == 5:
			self.time_preempt = 1200
			self.fade_in = 800
		else:
			self.time_preempt = 1200 - 750 * (self.ar - 5) / 5
			self.fade_in = 800 - 500 * (self.ar - 5) / 5
		self.opacity_interval = int(100 * self.interval / self.fade_in)

	def load_circle(self):
		self.overlay = CircleOverlay(self.overlay_filename, self.orig_cols, self.orig_rows)
		self.slidercircleoverlay = SliderCircleOverlay(self.slideroverlay_filename, self.orig_cols, self.orig_rows)
		self.radius_scale = self.cs * self.overlay_scale * 2 / default_size

	def overlayhitcircle(self, overlay, background, alpha=None):
		x1 = (background.size[0] - overlay.size[0]) // 2
		y1 = (background.size[1] - overlay.size[1]) // 2
		b = background.crop((x1, y1, x1 + overlay.size[0], y1 + overlay.size[1]))
		c = Image.alpha_composite(b, overlay)
		background.paste(c, (x1, y1))
		if alpha is not None:
			super().changealpha(background, alpha / 100)

	def prepare_circle(self):
		# prepare every single frame before entering the big loop, this will save us a ton of time since we don't need
		# to overlap number, circle overlay and approach circle every single time.

		# add color to circles
		for c in range(1, self.maxcolors + 1):
			color = self.colors["Combo" + str(c)]

			# add overlay to hitcircle
			orig_color_img = self.add_color(self.orig_img, color)
			orig_overlay_img = self.overlay.img.copy()
			self.overlayhitcircle(orig_overlay_img, orig_color_img)
			orig_overlay_img = super().change_size(self.radius_scale, self.radius_scale, img=orig_color_img)
			self.img = orig_overlay_img.copy()
			self.circle_frames.append([])

			# prepare fadeout frames
			self.circle_fadeout[0].append([])
			for x in range(100, 140, 4):
				size = x / 100
				im = super().newalpha(self.img, 1 - (x - 100) / 40)
				im = super().change_size(size, size, img=im)
				self.circle_fadeout[0][-1].append(im)

			orig_color_slider = super().add_color(self.slider_circle.orig_img, color)
			self.overlayhitcircle(self.slidercircleoverlay.img, orig_color_slider)
			orig_overlay_slider = super().change_size(self.radius_scale, self.radius_scale, img=orig_color_slider)
			self.slider_circle.img = orig_overlay_slider.copy()
			self.slidercircle_frames.append({})  # use dict to find the right combo will be faster

			# prepare fadeout frames
			self.circle_fadeout[1].append([])
			for x in range(100, 140, 4):
				size = x / 100
				im = super().newalpha(orig_overlay_slider, 1 - (x - 100) / 40)
				im = super().change_size(size, size, img=im)
				self.circle_fadeout[1][-1].append(im)

			# add number to circles
			for x in range(1, self.maxcombo[c] + 1):
				self.number_drawer.draw(self.img, x, self.overlap)

				# check if there is any slider with that number, so we can optimize the space by avoiding adding useless
				# slider frames
				if x in self.slider_combo:
					self.number_drawer.draw(self.slider_circle.img, x, self.overlap)
					self.slidercircle_frames[-1][x] = []

				alpha = 0  # alpha for fadein
				self.circle_frames[-1].append([])
				# we also overlay approach circle to circle to avoid multiple add_to_frame call
				for i in range(len(self.approachCircle.approach_frames)):
					approach_circle = super().add_color(self.approachCircle.approach_frames[i], color)
					# avoid useless slider frames
					if x in self.slider_combo:
						approach_slider = approach_circle.copy()
						self.overlayhitcircle(self.slider_circle.img, approach_slider, alpha)
						self.slidercircle_frames[-1][x].append(approach_slider)
					self.overlayhitcircle(self.img, approach_circle, alpha)
					self.circle_frames[-1][-1].append(approach_circle)
					alpha = min(100, alpha + self.opacity_interval)

				if x in self.slider_combo:
					self.slidercircle_frames[-1][x].append(self.slider_circle.img)
				self.circle_frames[-1][-1].append(self.img)  # for late tapping
				#
				self.img = orig_overlay_img.copy()
				self.slider_circle.img = orig_overlay_slider.copy()
		print("done")
		del self.approachCircle


# Slider
class ReverseArrow(AnimatableImage):
	def __init__(self, path, scale):
		AnimatableImage.__init__(self, path, reversearrow, scale, rotate=1)
		self.prepare_frames()

	def prepare_frames(self):
		for x in range(100, 80, -4):
			img = Images(self.path + self.filename, self.scale * x / 100, rotate=1)
			self.frames.append(img)
		self.n_frame = len(self.frames)


class SliderBall(AnimatableImage):
	def __init__(self, path, scale):
		AnimatableImage.__init__(self, path, sliderb, scale, hasframes=True)


class SliderFollow(AnimatableImage):
	def __init__(self, path, scale):
		AnimatableImage.__init__(self, path, sliderfollowcircle, scale, hasframes=True, delimiter="-")


class PrepareSlider(Images):
	def __init__(self, path, diff, scale, skin, movedown, moveright):
		self.path = path
		self.movedown = movedown
		self.moveright = moveright
		self.maxcolors = skin.colours["ComboNumber"]
		self.colors = skin.colours
		self.interval = 1000 / 60
		self.cs = (54.4 - 4.48 * diff["CircleSize"]) * scale

		self.scale = scale
		self.divide_by_255 = 1 / 255.0
		self.sliderb_frames = []
		self.sliderfollow_fadeout = []
		self.load_sliderballs()
		self.prepare_sliderball()

	def get_frames(self):
		return self.reversearrow, self.sliderb_frames, self.sliderfollow_fadeout, self.slidertick

	def load_sliderballs(self):
		self.radius_scale = self.cs * 2 / default_size

		self.reversearrow = ReverseArrow(self.path, self.radius_scale)
		self.sliderb = SliderBall(self.path, self.radius_scale)
		self.sliderfollowcircle = SliderFollow(self.path, self.radius_scale)

		self.followscale = default_size / self.sliderfollowcircle.pilimg_at(0).size[0]
		self.slidertick = Images(self.path + sliderscorepiont, self.radius_scale)

	def ballinhole(self, follow, sliderball):
		# still ned 4 channels so cannot do to_3channel before.

		# # if sliderfollowcircle is smaller than sliderball ( possible when fading in the sliderfollowcircle), then create
		# # a blank image with sliderball shape and put sliderfollowcircle at the center of that image.
		# if sliderball.shape[0] > follow.shape[0]:
		# 	new_img = np.zeros(sliderball.shape)
		# 	y1 = (new_img.size[1] / 2 - follow.size[1])//2
		# 	x1 = (new_img.size[0] / 2 - follow.size[0])//2
		# 	new_img.paste
		# 	follow = new_img

		#  find center
		y1 = (follow.size[1] - sliderball.size[1]) // 2
		x1 = (follow.size[0] - sliderball.size[0]) // 2

		follow.paste(sliderball, (x1, y1), sliderball)

	def prepare_sliderball(self):
		follow_fadein = 125  # sliderfollowcircle zoom out zoom in time

		for c in range(1, self.maxcolors + 1):
			color = self.colors["Combo" + str(c)]
			orig_color_sb = super().add_color(self.sliderb.pilimg_at(0), color)

			self.sliderb_frames.append([])

			scale_interval = round((1 - self.followscale) * self.interval / follow_fadein, 2)
			cur_scale = 1
			alpha_interval = round(self.interval / follow_fadein, 2)
			cur_alpha = 1

			for x in range(follow_fadein, 0, -int(self.interval)):
				orig_sfollow = super().newalpha(self.sliderfollowcircle.pilimg_at(0), cur_alpha)
				orig_sfollow = super().change_size(cur_scale, cur_scale, img=orig_sfollow)

				# add sliderball to sliderfollowcircle because it will optimize the render time since we don't need to
				# add to frame twice
				if c == 1:
					follow_img = orig_sfollow.copy()
					self.sliderfollow_fadeout.append(follow_img)

				self.ballinhole(orig_sfollow, orig_color_sb)
				self.sliderb_frames[-1].append(orig_sfollow.copy())
				# if it's the first loop then add sliderfollowcircle without sliderball for the fadeout
				cur_scale -= scale_interval
				cur_alpha -= alpha_interval


# Spinner
class PrepareSpinner(Images):
	def __init__(self, scale, path):
		self.divide_by_255 = 1 / 255.0
		self.scale = scale * 1.3 * 0.5
		self.path = path
		self.spinners = {}
		self.spinner_frames = []
		self.spinnermetre = []
		self.spinner_images = {}
		self.interval = 1000 / 60
		self.load_spinner()
		print("done loading spinner")
		self.prepare_spinner()
		print("done prepraing spinner")

	def get_frames(self):
		return self.spinner_images, self.spinnermetre, self.spinner_frames

	def load_spinner(self):
		print(self.scale)
		n = [spinnercircle, spinnerbackground, spinnerbottom, spinnerspin, spinnermetre, spinnerapproachcircle,
		     spinnertop]
		for img in n:
			self.spinner_images[img] = Images(self.path + img, self.scale)

	# self.to_square(self.spinner_images[spinnercircle])

	def prepare_spinner(self):
		for x in range(90):
			self.spinnermetre.append(self.spinner_images[spinnercircle].img.rotate(x))

		for x in range(10, -1, -1):
			width, height = self.spinner_images[spinnermetre].img.size
			height = int(height * x / 10)
			partial_metre = self.spinner_images[spinnermetre].img.copy()
			partial_metre.paste(Image.new("RGBA", (width, height)))

			# self.to_frame(new_img, self.spinner_images[spinnerbottom].img)
			self.spinner_frames.append(partial_metre)
