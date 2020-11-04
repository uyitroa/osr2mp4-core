from PIL import ImageFont, ImageDraw, Image
from osr2mp4 import logger
from osr2mp4.ImageProcess import imageproc
import os


def prepare_text(texts, size, color, settings, alpha=1, fontpath=""):
	size = int(size)
	
	try:
		font = ImageFont.truetype(fontpath, size=size)
	except Exception as e:
		font = ImageFont.load_default()
		logger.error(repr(e))

	img = Image.new("RGBA", (settings.width, settings.height))
	imgdraw = ImageDraw.Draw(img)
	imgs = {}
	for text in texts:
		img.paste((0, 0, 0, 0), (0, 0, img.size[0], img.size[1]))
		s = imgdraw.textsize(text, font=font)
		imgdraw.text((0, 0), text, color, font=font, spacing=size)
		imgs[text] = imageproc.newalpha(img.crop((0, 0, s[0], s[1])), alpha)

	return imgs
