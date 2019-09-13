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
		Images.__init__(self, filename, scale=circle_radius * 2 / default_circle_size)


class Number:
	def __init__(self, radius, path, default_circle_size):
		self.combo_number = []
		for x in range(10):
			self.combo_number.append(HitCircleNumber(path + "default-" + str(x), radius, default_circle_size))

	def draw(self, circle, number, gap):
		number = str(number)
		size = (-gap + self.combo_number[int(number[0])].buf.w) * (len(number) - 1)
		x_pos = circle.w // 2 - size // 2
		y_pos = circle.h // 2

		for digit in number:
			self.combo_number[int(digit)].add_to_frame(circle, x_pos, y_pos, channel=4)
			x_pos += -gap + self.combo_number[int(digit)].buf.w


class ApproachCircle(Images):
	def __init__(self, filename, scale, time_preempt, interval):
		Images.__init__(self, filename)
		self.scale = scale
		self.time_preempt = round(time_preempt)
		self.interval = int(interval)
		self.approach_frames = []
		self.prepare_sizes()

	def prepare_sizes(self):
		scale = 3.5
		for time_left in range(self.time_preempt, 0, -self.interval):
			scale -= 2.5 * self.interval / self.time_preempt
			buf = ImageBuffer(*self.change_size(scale * self.scale, scale * self.scale))
			self.approach_frames.append(buf)

	# # TODO: maybe delete?
	# def add_to_frame(self, background, x_offset, y_offset, time_left):
	# 	self.buf = self.approach_frames[int((self.time_preempt - time_left) / self.interval)]
	# 	super().add_to_frame(background, x_offset, y_offset, channel=4)


class CircleOverlay(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)


class SliderCircleOverlay(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)


class CircleSlider(Images):
	def __init__(self, filename):
		Images.__init__(self, filename)


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
		self.gap = int(skin.fonts["HitCircleOverlap"] * self.radius_scale)

		self.slider_combo = beatmap.slider_combo
		self.slider_circle = CircleSlider(path + sliderstartcircle)

		self.number_drawer = Number(self.cs * 0.9, path, default_size)
		self.approachCircle = ApproachCircle(path + approachcircle, self.radius_scale,
		                                     self.time_preempt, self.interval)

		self.circle_frames = []
		self.slidercircle_frames = []
		self.circle_fadeout = [[], []]
		self.prepare_circle()

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
		self.overlay = CircleOverlay(self.overlay_filename)
		self.slidercircleoverlay = SliderCircleOverlay(self.slideroverlay_filename)
		self.radius_scale = self.cs * self.overlay_scale * 2 / default_size

	def overlayhitcircle(self, overlay, circle_buf):
		self.ensureBGsize(circle_buf, overlay)
		# still ned 4 channels so cannot do to_3channel before.
		y1 = np.int32(circle_buf.h / 2 - overlay.h / 2)
		x1 = np.int32(circle_buf.w / 2 - overlay.w / 2)

		self.prg.add_to_frame4(self.queue, (overlay.h, overlay.w), None, overlay.img, circle_buf.img, overlay.w, overlay.pix, circle_buf.w,
		                       circle_buf.pix, x1, y1, np.int32(0), np.int32(0), np.float32(1))

	def overlay_approach(self, background, x_offset, y_offset, circle_buf):
		y1, y2 = y_offset - int(circle_buf.h / 2), y_offset + int(circle_buf.h / 2)
		x1, x2 = x_offset - int(circle_buf.w / 2), x_offset + int(circle_buf .w / 2)

		y1, y2, ystart, yend = super().checkOverdisplay(y1, y2, background.h)
		x1, x2, xstart, xend = super().checkOverdisplay(x1, x2, background.w)


		self.prg.add_to_frame4(self.queue, (y2-y1, x2-x1), None, circle_buf.img, background.img, circle_buf.w, circle_buf.pix,
		                       background.w, background.pix, x1, y1, np.int32(0), np.int32(0), np.float32(1))


	def prepare_circle(self):
		# prepare every single frame before entering the big loop, this will save us a ton of time since we don't need
		# to overlap number, circle overlay and approach circle every single time.

		color_circle = ImageBuffer()
		color_slider = ImageBuffer()
		circle_buf = ImageBuffer()  # actual buffer for the hitcircle.png + hitcircleoverlay.png
		slider_buf = ImageBuffer()  # actual buffer for the slidercircle.png + slideroverlau.png
		im = ImageBuffer()  # circle fadeout buffer
		ims = ImageBuffer()  # slider circle fadeout buffer

		# add color to circles
		for c in range(1, self.maxcolors + 1):
			color = self.colors["Combo" + str(c)]

			# add overlay to hitcircle
			# TODO: combine every kernel to avoid multiple unnecessary gpu call
			color_circle.set(super().add_color(color, buf=self.buf, new_dst=True), *self.buf.shape())
			self.overlayhitcircle(self.overlay.buf, color_circle)
			circle_buf.set(*super().change_size(self.radius_scale, self.radius_scale, buf=color_circle))
			self.circle_frames.append([])

			# prepare fadeout frames
			im.set(None, *circle_buf.shape())
			self.circle_fadeout[0].append([])
			for x in range(100, 140, 4):
				size = x / 100
				im.img = super().edit_channel(3, 1 - (x - 100) / 40, buf=circle_buf, new_dst=True)
				imgbuf = ImageBuffer(*super().change_size(size, size, buf=im))
				self.circle_fadeout[0][-1].append(imgbuf)


			color_slider.set(super().add_color(color, buf=self.slider_circle.buf, new_dst=True), *self.slider_circle.buf.shape())
			self.overlayhitcircle(self.slidercircleoverlay.buf, color_slider)
			slider_buf.set(*super().change_size(self.radius_scale, self.radius_scale, buf=color_slider))
			self.slidercircle_frames.append({})  # use dict to find the right combo will be faster

			# prepare fadeout frames
			ims.set(None, *slider_buf.shape())
			self.circle_fadeout[1].append([])
			for x in range(100, 140, 4):
				size = x / 100
				ims.img = super().edit_channel(3, 1 - (x - 100) / 40, buf=slider_buf, new_dst=True)
				imgbuf = ImageBuffer(*super().change_size(size, size, buf=ims))
				self.circle_fadeout[1][-1].append(imgbuf)


			raw_circle_buf = ImageBuffer(super().copy_img(circle_buf), *circle_buf.shape())  # without number
			raw_slider_buf = ImageBuffer(super().copy_img(slider_buf), *slider_buf.shape())

			# add number to circles
			for x in range(1, self.maxcombo[c] + 1):
				self.number_drawer.draw(circle_buf, x, self.gap)

				# check if there is any slider with that number, so we can optimize the space by avoiding adding useless
				# slider frames
				if x in self.slider_combo:
					self.number_drawer.draw(slider_buf, x, self.gap)
					self.slidercircle_frames[-1][x] = []

				alpha = 0  # alpha for fadein
				self.circle_frames[-1].append([])
				# we also overlay approach circle to circle to avoid multiple add_to_frame call
				for i in range(len(self.approachCircle.approach_frames)):
					approach_circle = ImageBuffer()
					approach_circle.img = super().add_color(color, buf=self.approachCircle.approach_frames[i], new_dst=True)
					approach_circle.set_shape(*self.approachCircle.approach_frames[i].shape())

					x_offset = approach_circle.w//2
					y_offset = approach_circle.h//2

					# avoid useless slider frames
					if x in self.slider_combo:
						approach_slider = ImageBuffer()
						approach_slider.img = super().copy_img(buf=approach_circle)
						approach_slider.set_shape(*approach_circle.shape())

						self.overlay_approach(approach_slider, x_offset, y_offset, slider_buf)
						self.edit_channel(3, alpha / 100, buf=approach_circle)
						self.slidercircle_frames[-1][x].append(approach_slider)

					self.overlay_approach(approach_circle, x_offset, y_offset, circle_buf)
					self.edit_channel(3, alpha/100, buf=approach_circle)
					self.circle_frames[-1][-1].append(approach_circle)

					alpha = min(100, alpha + self.opacity_interval)

				if x in self.slider_combo:
					self.slidercircle_frames[-1][x].append(slider_buf)
				self.circle_frames[-1][-1].append(circle_buf)  # for late tapping

				circle_buf = ImageBuffer(super().copy_img(raw_circle_buf), *circle_buf.shape())
				slider_buf = ImageBuffer(super().copy_img(raw_slider_buf), *slider_buf.shape())
		print("done")
		del self.approachCircle


# Slider
class ReverseArrow(AnimatableImage):
	def __init__(self, path, scale):
		AnimatableImage.__init__(self, path, reversearrow, scale, rotate=1)
		self.prepare_frames()

	def prepare_frames(self):
		for x in range(100, 80, -4):
			img = Images(self.path + self.filename, self.scale * x / 10, rotate=1)
			self.frames.append(img.buf)
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

		self.followscale = default_size / self.sliderfollowcircle.buffer_at(0).shape()[0]
		self.slidertick = Images(self.path + sliderscorepiont, self.radius_scale)

	def ballinhole(self, follow, sliderball):
		# still ned 4 channels so cannot do to_3channel before.

		# if sliderfollowcircle is smaller than sliderball ( possible when fading in the sliderfollowcircle), then create
		# a blank image with sliderball shape and put sliderfollowcircle at the center of that image.
		super().ensureBGsize(follow, sliderball)

		#  find center
		y1= np.int32(follow.h / 2 - sliderball.h / 2)
		x1 = np.int32(follow.w / 2 - sliderball.w / 2)

		zero = np.int32(0)
		self.prg.add_to_frame4(self.queue, (sliderball.h, sliderball.w), None, sliderball.img, follow.img, sliderball.w, sliderball.pix, follow.w, follow.pix, x1, y1, zero, zero, np.float32(1))

	def prepare_sliderball(self):
		follow_fadein = 125  # sliderfollowcircle zoom out zoom in time

		color_sb = ImageBuffer()
		sfollow = ImageBuffer()

		for c in range(1, self.maxcolors + 1):
			color = self.colors["Combo" + str(c)]
			color_sb.set(super().copy_img(self.sliderb.buffer_at(0)), *self.sliderb.buffer_at(0).shape())
			super().add_color(color, buf=color_sb)

			self.sliderb_frames.append([])

			scale_interval = round((1 - self.followscale) * self.interval / follow_fadein, 2)
			cur_scale = 1
			alpha_interval = round(self.interval / follow_fadein, 2)
			cur_alpha = 1

			for x in range(follow_fadein, 0, -int(self.interval)):
				sfollow = ImageBuffer(*super().change_size(cur_scale, cur_scale, buf=self.sliderfollowcircle.buffer_at(0)))
				super().edit_channel(3, cur_alpha, buf=sfollow)

				# add sliderball to sliderfollowcircle because it will optimize the render time since we don't need to
				# add to frame twice
				if c == 1:
					follow_img = ImageBuffer(super().copy_img(sfollow), *sfollow.shape())
					self.sliderfollow_fadeout.append(follow_img)

				self.ballinhole(sfollow, color_sb)
				self.sliderb_frames[-1].append(sfollow)
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
		self.spinner_images[spinnercircle].to_3channel()
		self.spinner_images[spinnerbackground].to_3channel()

		for x in range(90):
			self.spinnermetre.append(
				transform.rotate(self.spinner_images[spinnercircle].img, x, preserve_range=True, order=0).astype(
					np.uint8))

		for x in range(10, -1, -1):
			height, width, a = self.spinner_images[spinnermetre].img.shape
			height = int(height * x / 10)
			partial_metre = np.copy(self.spinner_images[spinnermetre].img)
			partial_metre[:height, :, :] = np.zeros((height, width, 4))[:, :, :]

			# self.to_frame(new_img, self.spinner_images[spinnerbottom].img)
			self.orig_img = np.copy(partial_metre)
			self.to_3channel()
			self.spinner_frames.append(self.orig_img)
