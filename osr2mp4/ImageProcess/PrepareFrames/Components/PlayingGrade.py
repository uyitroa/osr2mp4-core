from PIL import Image

from ... import imageproc

from ...Animation.alpha import fadeout

from ...Animation.size import grow

from ...PrepareFrames.YImage import YImage

ranking = "ranking-"


def prepare_playinggrade(scale, settings):
	frames = []

	grades = ["XH", "SH", "X", "S", "A", "B", "C", "D"]
	for grade in grades:
		img = YImage(ranking + grade + "-small", settings, scale).img
		step = settings.timeframe/1000 * 60/settings.fps
		effects = grow(img, 1, 2, step * 0.05)
		effects = fadeout(effects, 1, 0, step * 0.05)
		for x in effects:
			imageproc.add(img, x, x.size[0]/2, x.size[1]/2, channel=4)
		effects.append(img)
		frames.append(effects)

	# frameshd = [YImage(ranking + "XH-small", settings, scale).img, YImage(ranking + "SH-small", settings, scale).img]
	# frameshd.extend(frames[2:])
	framesnm = frames[2:]
	frameshd = frames[:2] + frames[4:]

	return framesnm, frameshd
