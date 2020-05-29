from ...PrepareFrames.YImage import YImage

section_pass = "section-pass"
section_fail = "section-fail"


def prepare_sections(scale):
	"""
	:param scale: float
	:return: [PIL.Image]
	"""
	spass = YImage(section_pass, scale).img
	sfail = YImage(section_fail, scale).img
	frame = [sfail, spass]
	return frame
