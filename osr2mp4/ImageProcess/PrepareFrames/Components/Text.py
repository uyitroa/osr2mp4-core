from PIL import ImageFont, ImageDraw, Image

from ....global_var import Settings, Paths


def prepare_text(texts, size, color):
	size = int(size)
	font = ImageFont.truetype(Paths.path + "res/Arial.ttf", size=size)

	img = Image.new("RGBA", (Settings.width, Settings.height))
	imgdraw = ImageDraw.Draw(img)
	imgs = {}
	for text in texts:
		img.paste((0, 0, 0, 0), (0, 0, img.size[0], img.size[1]))
		s = imgdraw.textsize(text, font=font)
		imgdraw.text((0, 0), text, color, font=font, spacing=size)
		imgs[text] = img.crop((0, 0, s[0], s[1]))

	return imgs

