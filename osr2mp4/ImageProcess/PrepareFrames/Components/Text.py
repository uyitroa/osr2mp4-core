from PIL import ImageFont, ImageDraw, Image
from ... import imageproc


def prepare_text(texts, size, color, settings, alpha=1):
	size = int(size)
	font = ImageFont.truetype(settings.path + "res/Aller_Rg.ttf", size=size)

	img = Image.new("RGBA", (settings.width, settings.height))
	imgdraw = ImageDraw.Draw(img)
	imgs = {}
	for text in texts:
		img.paste((0, 0, 0, 0), (0, 0, img.size[0], img.size[1]))
		s = imgdraw.textsize(text, font=font)
		imgdraw.text((0, 0), text, color, font=font, spacing=size)
		imgs[text] = imageproc.newalpha(img.crop((0, 0, s[0], s[1])), alpha)

	return imgs

