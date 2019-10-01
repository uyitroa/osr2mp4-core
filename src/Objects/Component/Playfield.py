from Objects.abstracts import Images

FORMAT = ".png"


class Playfield(Images):
	def __init__(self, filename, width, height):
		Images.__init__(self, filename)

	def add_to_frame(self, background):
		super().add_to_frame(background, 0, 0)


