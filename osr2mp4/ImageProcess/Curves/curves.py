from osr2mp4.ImageProcess.Curves.libcurves.ccurves import create_curve, get_pos_at


class Curve:
	def __init__(self, slider_type, control_points, expect_length):
		self.slider_type = slider_type
		self.control_points = control_points
		self.pos, self.cum_length = create_curve(slider_type, control_points, expect_length)

	def at(self, distance):
		# if t is not None:
		# 	dist = self.cum_length[-1] * t
		pos = get_pos_at(self.pos, self.cum_length, distance)
		return pos


def getclass(slidertype, points, pixellength):
	return Curve(slidertype, points, pixellength)
