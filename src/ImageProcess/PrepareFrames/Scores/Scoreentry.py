from PIL import ImageDraw, Image

from EEnum.EImageFrom import ImageFrom
from ImageProcess import imageproc
from ImageProcess.PrepareFrames.YImage import YImage


scoreentry = "scoreentry-"


def prepare_scoreboardscore(scale):
	"""
	:param path: string of path, without filename
	:param scale: float
	:param color: tuple(R, G, B)
	:return: [PIL.Image]
	"""
	numbers_animation = []
	for x in range(12):
		if x == 10:
			x = "x"
		if x == 11:
			x = "dot"
		number = YImage(scoreentry + str(x), scale * 0.8)
		if x == "dot":
			x = "."
		if number.imgfrom == ImageFrom.BLANK:
			img = Image.new("RGBA", (14, 14))
			imagedraw = ImageDraw.Draw(img)
			size = imagedraw.getfont().getsize(str(x))
			imagedraw.text((0, 0), str(x), (255, 255, 255, 255))
			img = imageproc.change_size(img.crop((0, 0, size[0], size[1])), scale * 1.3, scale * 1.3)
		else:
			img = number.img

		numbers_animation.append(img)
	combo_number = imageproc.change_sizes(numbers_animation, 0.9, 0.9)
	combo_number = imageproc.add_color_s(combo_number, [200, 255, 255])
	bigger_numbers_animation = imageproc.change_sizes(numbers_animation, 2, 2)
	return numbers_animation, bigger_numbers_animation, combo_number
