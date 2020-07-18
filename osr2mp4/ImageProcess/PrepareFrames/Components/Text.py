import logging

from PIL import ImageFont, ImageDraw, Image
from ... import imageproc
import os


def prepare_text(texts, size, color, settings, alpha=1, fontpath=""):
	if fontpath == "":
		fontpath = os.path.join(settings.path, "res/Aller_Rg.ttf")
	size = int(size)
	try:
		font = ImageFont.truetype(fontpath, size=size)
	except Exception as e:
		font = ImageFont.truetype(os.path.join(settings.path, "res/Aller_Rg.ttf"), size=size)
		logging.error(repr(e))

	img = Image.new("RGBA", (settings.width, settings.height))
	imgdraw = ImageDraw.Draw(img)
	imgs = {}
	for text in texts:
		img.paste((0, 0, 0, 0), (0, 0, img.size[0], img.size[1]))
		s = imgdraw.textsize(text, font=font)
		imgdraw.text((0, 0), text, color, font=font, spacing=size)
		imgs[text] = imageproc.newalpha(img.crop((0, 0, s[0], s[1])), alpha)

	return imgs

