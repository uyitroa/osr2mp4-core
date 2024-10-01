import json
from PIL import ImageFont, ImageDraw, Image
from osr2mp4 import logger
from osr2mp4.ImageProcess import imageproc
import os


def prepare_text(texts: list, size: int, color: list, settings: object, alpha: int = 1, fontpath: str = ""):
	if fontpath == "":
		fontpath = os.path.join(settings.path, "res/Aller_Rg.ttf")

	# weird bug where osr2mp4-app gives color a stringified list for some fucking reason
	if isinstance(color, str):
		color = json.loads(color) # i couldve just do eval(color) but someone could just put some bullshit code in that and fuck the user somehow
	
	size = int(size)
	color = tuple(color)
	
	
	try:
		font = ImageFont.truetype(fontpath, size=size)
	except Exception as e:
		font = ImageFont.truetype(os.path.join(settings.path, "res/Aller_Rg.ttf"), size=size)
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
