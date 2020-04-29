from ImageProcess.PrepareFrames.YImage import YImage

spinnercircle = "spinner-circle"
spinnerbackground = "spinner-background"
spinnerbottom = "spinner-bottom"
spinnerspin = "spinner-spin"
spinnermetre = "spinner-metre"
spinnerapproachcircle = "spinner-approachcircle"
spinnertop = "spinner-top"


def prepare_spinner(path, scale):
	scale = scale * 1.3 * 0.5
	path = path
	spinner_images = {}
	n = [spinnercircle, spinnerbackground, spinnerbottom, spinnerspin, spinnermetre, spinnerapproachcircle,
	     spinnertop]
	for img in n:
		spinner_images[img] = YImage(path + img, scale).img
	return spinner_images
