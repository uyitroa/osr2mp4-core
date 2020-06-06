from ...PrepareFrames.YImage import YImage

section_pass = "section-pass"
section_fail = "section-fail"


def prepare_sections(scale, settings):
	"""
	:param settings:
	:param scale: float
	:return: [PIL.Image]
	"""
	spass = YImage(section_pass, settings, scale).img
	sfail = YImage(section_fail, settings, scale).img
	frame = [sfail, spass]
	return frame
