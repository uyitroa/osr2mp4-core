from PIL import Image

from ImageProcess.PrepareFrames.YImage import YImage
from global_var import Settings

scorebarbg = "scorebar-bg"


def prepare_scorebarbg(scale, backgroundframe):
	"""
	:param scale: float
	:return: [PIL.Image]
	"""
	img = YImage(scorebarbg, scale).img
	img2 = Image.new("RGBA", (Settings.width, Settings.height), (0, 0, 0, 255))

	img2.paste(img, (0, 0), mask=img)
	return [img, img2]

