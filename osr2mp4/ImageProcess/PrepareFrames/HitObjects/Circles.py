
# Circle
from PIL import Image
import numpy as np

from osr2mp4 import logger
from osr2mp4.EEnum.EImageFrom import ImageFrom
from osr2mp4.ImageProcess import imageproc
from osr2mp4.ImageProcess.Animation import alpha, size
from osr2mp4.ImageProcess.PrepareFrames.YImage import YImage, YImages
from osr2mp4.ImageProcess.imageproc import newalpha
from osr2mp4.ImageProcess.Animation import easings

hitcircle = "hitcircle"
hitcircleoverlay = "hitcircleoverlay"
sliderstartcircleoverlay = "sliderstartcircleoverlay"
sliderstartcircle = "sliderstartcircle"
approachcircle = "approachcircle"

default_size = 128
overlay_scale = 1.05


def prepare_approach(scale, time_preempt, settings):
	"""
	:param settings:
	:param scale: float
	:param time_preempt: the time the circle is on screen
	:return: [PIL.Image]
	"""
	img = YImage(approachcircle, settings).img
	approach_frames = [] # 27 frames on 60 fps

	s = 3.5
	interval = settings.timeframe / settings.fps
	for time_left in np.arange(time_preempt, 0, -interval):
		s -= 2.5 * interval / time_preempt
		p = imageproc.change_size(img, s * scale, s * scale)
		approach_frames.append(p)
	
	return approach_frames


def overlayhitcircle(overlay, circle, color, scale):	
	color_circle = imageproc.add_color(circle, color)

	maxwidth = max(color_circle.size[0], overlay.size[0])
	maxheight = max(color_circle.size[1], overlay.size[1])

	background = Image.new("RGBA", (maxwidth, maxheight))
	background.paste(color_circle, (maxwidth//2 - color_circle.size[0]//2, maxheight//2 - color_circle.size[1]//2))
	color_circle = background

	overlay_img = overlay.copy()

	x1 = color_circle.size[0] // 2
	y1 = color_circle.size[1] // 2

	imageproc.add(overlay_img, color_circle, x1, y1, channel=4)
	return imageproc.change_size(color_circle, scale, scale)


def overlayapproach(circle, approach, alpha):

	maxwidth = max(approach.size[0], circle.size[0])
	maxheight = max(approach.size[1], circle.size[1])

	background = Image.new("RGBA", (maxwidth, maxheight))
	background.paste(approach, (maxwidth//2 - approach.size[0]//2, maxheight//2 - approach.size[1]//2))
	approach = background

	x1 = approach.size[0] // 2
	y1 = approach.size[1] // 2

	imageproc.add(circle, approach, x1, y1, channel=4)
	return imageproc.newalpha(approach, alpha/100)


def prepare_fadeout(img, settings):
	# 240ms cuz https://github.com/Wieku/danser-go/blob/23a5137c5c4069bd1f39a9e920065fce4614a6aa/app/beatmap/difficulty/difficulty.go#L7
	fade_out = alpha.fade(img, 1, 0, 240, settings, easings.easeOutQuad)
	fade_out = size.resize(fade_out, 1, 1.4, 240, settings, easings.easeOutQuad)
	return fade_out


def calculate_ar(ar, settings):
	interval = settings.timeframe / settings.fps
	if ar < 5:
		time_preempt = 1200 + 600 * (5 - ar) / 5
		fade_in = 800 + 400 * (5 - ar) / 5
	elif ar == 5:
		time_preempt = 1200
		fade_in = 800
	else:
		time_preempt = 1200 - 750 * (ar - 5) / 5
		fade_in = 800 - 500 * (ar - 5) / 5
	opacity_interval = 100 * interval / fade_in
	return opacity_interval, time_preempt, fade_in


def load(settings):
	circle = YImage(hitcircle, settings).img
	c_overlay = YImages(hitcircleoverlay, settings, delimiter="-").frames[0]
	yslider = YImage(sliderstartcircle, settings, fallback=hitcircle)
	slider = yslider.img
	slideroverlay = sliderstartcircleoverlay
	if yslider.imgfrom == ImageFrom.FALLBACK_X or yslider.imgfrom == ImageFrom.FALLBACK_X2:
		slideroverlay = hitcircleoverlay
	s_overlay = YImage(slideroverlay, settings, fallback=hitcircleoverlay).img
	return circle, c_overlay, slider, s_overlay


def prepare_circle(diff, scale, settings, hd):
	# prepare every single frame before entering the big loop, this will save us a ton of time since we don't need
	# to overlap number, circle overlay and approach circle every single time.

	opacity_interval, time_preempt, fade_in = calculate_ar(diff["ApproachRate"], settings)

	cs = (54.4 - 4.48 * diff["CircleSize"]) * scale
	radius_scale = cs * overlay_scale * 2 / default_size

	circle, c_overlay, slider, s_overlay = load(settings)
	if not hd:
		approach_frames = prepare_approach(radius_scale, time_preempt, settings)

	fadeout = [[], []]  # circle, slider
	circle_frames = []  # [color][number][alpha]
	slidercircle_frames = []  # [color][number][alpha]
	alphas = []

	for c in range(1, settings.skin_ini.colours["ComboNumber"] + 1):
		color = settings.skin_ini.colours["Combo" + str(c)]

		orig_circle = overlayhitcircle(c_overlay, circle, color, radius_scale)

		if not hd:
			fadeout[0].append(prepare_fadeout(orig_circle, settings))
		else:
			fadeout[0].append([Image.new("RGBA", (1, 1))])

		orig_slider = overlayhitcircle(s_overlay, slider, color, radius_scale)

		if not hd:
			fadeout[1].append(prepare_fadeout(orig_slider, settings))
		else:
			fadeout[1].append([Image.new("RGBA", (1, 1))])

		alpha = 0  # alpha for fadein
		circle_frames.append([])
		slidercircle_frames.append([])
		if not hd:

			# we also overlay approach circle to circle to avoid multiple add_to_frame call
			for i in range(len(approach_frames)):
				approach_circle = imageproc.add_color(approach_frames[i], color)
				approach_slider = approach_circle.copy()

				circle_frames[-1].append(overlayapproach(orig_circle, approach_circle, alpha))
				slidercircle_frames[-1].append(overlayapproach(orig_slider, approach_slider, alpha))

				alphas.append(alpha)
				alpha = min(100, alpha + opacity_interval)
			# for late tapping
			slidercircle_frames[-1].append(orig_slider)
			circle_frames[-1].append(orig_circle)
			alphas.append(alpha)

		else:
			# source: https://github.com/ppy/osu/blob/4cb57f8205edf5ed7b7da076325ba76ec9cc3039/osu.Game.Rulesets.Osu/Mods/OsuModHidden.cs#L23
			interval = settings.timeframe / settings.fps
			fade_in = time_preempt * 0.4
			fade_in_interval = 100 * interval/fade_in

			ii = fade_in_interval

			fade_out = time_preempt * 0.3
			fade_out_interval = 100 * interval/fade_out

			#interval = 1 if not interval else interval
			for i in np.arange(time_preempt, 0, -interval):
				if alpha != 0:
					circle_frames[-1].append(newalpha(orig_circle, alpha/100))
					slidercircle_frames[-1].append(newalpha(orig_slider, alpha/100))
				else:
					circle_frames[-1].append(Image.new("RGBA", (1, 1)))
					slidercircle_frames[-1].append(Image.new("RGBA", (1, 1)))

				if alpha == 100:
					ii = -fade_out_interval

				alphas.append(alpha)
				alpha = max(0, min(100, alpha + ii))

		logger.debug("done")

	return slidercircle_frames, circle_frames, fadeout, alphas
