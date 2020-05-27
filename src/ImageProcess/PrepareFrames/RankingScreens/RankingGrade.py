from ...PrepareFrames.YImage import YImage

ranking = "ranking-"


def prepare_rankinggrade(scale):
	frames = []

	grades = ["X", "S", "A", "B", "C", "D"]
	for grade in grades:
		frames.append(YImage(ranking + grade, scale).img)

	return frames
