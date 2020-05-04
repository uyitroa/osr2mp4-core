from PIL import Image

from ImageProcess import imageproc
from ImageProcess.PrepareFrames.YImage import YImage, YImages

sliderb = "sliderb"
sliderfollowcircle = "sliderfollowcircle"
sliderscorepoint = "sliderscorepoint"
reversearrow = "reversearrow"
default_size = 128


def ballinhole(follow, sliderball):

	if follow.size[0] < sliderball.size[0] or follow.size[1] < sliderball.size[1]:
		width, height = max(follow.size[0], sliderball.size[0]), max(follow.size[1], sliderball.size[1])
		f = Image.new("RGBA", (width, height))
		imageproc.add(follow, f, width//2, height//2)
		follow = f

	y1 = (follow.size[1] - sliderball.size[1]) // 2
	x1 = (follow.size[0] - sliderball.size[0]) // 2

	follow.paste(sliderball, (x1, y1), sliderball)
	return follow


def load(scale):
	arrow_frames = []
	for x in range(120, 100, -4):
		img = YImage(reversearrow, scale * x / 100, rotate=1)
		arrow_frames.append(img.img)

	sliderb_frames = YImages(sliderb, scale).frames
	sliderfollow_frames = YImages(sliderfollowcircle, scale).frames
	slider_tick = YImage(sliderscorepoint, scale).img
	return arrow_frames, sliderb_frames, sliderfollow_frames, slider_tick


def prepare_slider(diff, scale, skin, settings):

	cs = (54.4 - 4.48 * diff["CircleSize"]) * scale
	radius_scale = cs * 2 / default_size

	interval = settings.timeframe / settings.fps
	follow_fadein = 150  # need 150ms to fadein

	arrow_frames, sliderb_frames, sliderfollow_frames, slider_tick = load(radius_scale)

	sframes = []
	sliderfollow_fadeout = []

	for c in range(1, skin.colours["ComboNumber"] + 1):
		color = skin.colours["Combo" + str(c)]
		color_sb = imageproc.add_color(sliderb_frames[0], color)

		sframes.append([])

		scale_interval = round(0.35 * interval/follow_fadein, 2)
		print(scale_interval)
		cur_scale = 1
		alpha_interval = round(interval / follow_fadein, 2)
		cur_alpha = 1

		for x in range(follow_fadein, 0, -int(interval)):
			sfollow = imageproc.newalpha(sliderfollow_frames[0], cur_alpha)
			sfollow = imageproc.change_size(sfollow, cur_scale, cur_scale)

			# add sliderball to sliderfollowcircle because it will optimize the render time since we don't need to
			# add to frame twice
			if c == 1:
				follow_img = sfollow.copy()
				sliderfollow_fadeout.append(follow_img)

			sfollow = ballinhole(sfollow, color_sb)
			sframes[-1].append(sfollow)

			# if it's the first loop then add sliderfollowcircle without sliderball for the fadeout
			cur_scale -= scale_interval
			cur_alpha -= alpha_interval

	return arrow_frames, sframes, sliderfollow_fadeout, slider_tick
