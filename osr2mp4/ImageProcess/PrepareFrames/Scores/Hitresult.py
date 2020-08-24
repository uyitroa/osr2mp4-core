from math import sin, cos

from PIL import Image

from osr2mp4.ImageProcess import imageproc
from osr2mp4.EEnum.EImageFrom import ImageFrom
from osr2mp4.ImageProcess.Animation import size
from osr2mp4.ImageProcess.PrepareFrames.YImage import YImages, YImage

hitprefix = "hit"
particleprefix = "particle"
default_size = 128
hitresult_size = 1.5


def prepare_hitresults(scale, diff, settings):

	cs = (54.4 - 4.48 * diff["CircleSize"]) * scale
	scale = cs * 2 * hitresult_size / default_size

	particles_frames = prepare_particles(scale, settings)

	scores_frames = {}
	singleframemiss = False
	for x in [0, 50, 100, 300]:
		yimg = YImages(hitprefix + str(x), settings, scale, delimiter="-", rotate=x == 0)
		f = []
		f1 = yimg.frames
		if yimg.unanimate or len(yimg.frames) == 1:
			img = yimg.frames[0]
			f = []
			if x != 0:
				f = size.grow(img, 0.7, 1.1, 0.05)

		if x == 0:
			if yimg.unanimate or len(yimg.frames) == 1:
				f1 = f1[0]
				f1 = size.shrink(f1, 1.45, 0.9, 0.05)
			f = []
			singleframemiss = len(yimg.frames) == 1

		if x in particles_frames:
			f = []
			f1 = particles_frames[x]
		scores_frames[x] = f+f1
	return scores_frames, singleframemiss


def pseudorandom(n):
	if n % 4 == 0:
		xdir = 1
		ydir = 1
	elif n % 4 == 1:
		xdir = 1
		ydir = -1
	elif n % 4 == 0:
		xdir = -1
		ydir = 1
	else:
		xdir = -1
		ydir = -1

	if n <= 20:
		xdir /= 10
		ydir /= 10

	if n % 2 == 0:
		return xdir * sin(n/20+n/100) * ((n+1)%5+1)/5, ydir * cos(n/20) * (n%5+1)/5
	else:
		return xdir * sin(n / 20) * (n % 5 + 1) / 5, ydir * cos(n / 20+n/100) * ((n+1) % 5 + 1) / 5


def prepare_particles(scale, settings):
	frames = {}
	for hit in [50, 100]:
		yimg = YImage(particleprefix + str(hit), settings, scale)
		if yimg.imgfrom == ImageFrom.DEFAULT_X or yimg.imgfrom == ImageFrom.DEFAULT_X2 or yimg.imgfrom == ImageFrom.BLANK:
			continue

		fr = []
		sizee = int(150 * scale)
		f = [[sizee / 2, sizee / 2, 100] for i in range(100)]
		for z in range(120):
			background = Image.new("RGBA", (sizee, sizee), (0, 0, 0, 0))
			for b in range(len(f)):
				pos = f[b]
				x, y = pseudorandom(b)
				pos[0] += x * scale
				pos[1] += y * scale
				pos[2] -= max(1, (abs(x) + abs(y)) * 1.25)
				imageproc.add(yimg.img, background, pos[0], pos[1], alpha=max(0.0, min(1.0, pos[2]/100)), channel=4)
			if z > 3:
				fr.append(background)
				# background.save(f"test{z}.png")

		frames[hit] = fr

	return frames
