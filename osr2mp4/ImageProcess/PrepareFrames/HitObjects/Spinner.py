from PIL import Image

from osr2mp4.EEnum.EImageFrom import ImageFrom
from ... import imageproc
from ...PrepareFrames.YImage import YImage

spinnercircle = "spinner-circle"
spinnerbackground = "spinner-background"
spinnermiddle = "spinner-middle"
spinnermiddle2 = "spinner-middle2"
spinnerspin = "spinner-spin"
spinnermetre = "spinner-metre"
spinnerapproachcircle = "spinner-approachcircle"
spinnerbottom = "spinner-bottom"
spinnerrpm = "spinner-rpm"


def prepare_spinner(scale, settings):
	scale = scale * 1.3 * 0.5
	spinner_images = {}
	n = [spinnercircle, spinnerbackground, spinnermiddle, spinnermiddle2, spinnerspin, spinnermetre, spinnerbottom, spinnerrpm]

	spinv2 = False
	for img in n:
		yimage = YImage(img, settings, scale)
		spinner_images[img] = imageproc.newalpha(yimage.img, 0.75)
		if img == spinnerbackground and yimage.imgfrom == ImageFrom.BLANK:
			spinv2 = True

	if spinv2:
		spinner_images[spinnerbackground] = spinner_images[spinnermiddle]

		maxwidth = max(spinner_images[spinnerbottom].size[0], spinner_images[spinnermiddle2].size[0])
		maxheight = max(spinner_images[spinnerbottom].size[1], spinner_images[spinnermiddle2].size[1])
		circle = Image.new("RGBA", (maxwidth, maxheight))
		imageproc.add(spinner_images[spinnermiddle2], circle, circle.size[0]/2, circle.size[1]/2, channel=4)
		imageproc.add(spinner_images[spinnerbottom], circle, circle.size[0]/2, circle.size[1]/2, channel=4)
		spinner_images[spinnercircle] = circle

		spinner_images[spinnermetre] = Image.new("RGBA", (1, 1))

	return spinner_images
