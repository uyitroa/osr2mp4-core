from ImageProcess.PrepareFrames.YImage import YImage

spinnercircle = "spinner-circle"
spinnerbackground = "spinner-background"
spinnerbottom = "spinner-bottom"
spinnerspin = "spinner-spin"
spinnermetre = "spinner-metre"
spinnerapproachcircle = "spinner-approachcircle"
spinnertop = "spinner-top"


def prepare_spinner(scale):
	scale = scale * 1.3 * 0.5
	spinner_images = {}
	n = [spinnercircle, spinnerbackground, spinnerbottom, spinnerspin, spinnermetre, spinnerapproachcircle,
	     spinnertop]
	for img in n:
		spinner_images[img] = YImage(img, scale).img
	return spinner_images
