from PIL import Image

from ... import imageproc
from ...PrepareFrames.YImage import YImage
from ....global_var import SkinPaths

rankingpanel = "ranking-panel"


def prepare_rankingpanel(scale, background):
	"""
	:param scale: float
	:param background: PIL.Image
	:return: [PIL.Image]
	"""
	yimg = YImage(rankingpanel, scale)
	img = yimg.img

	blackbar = Image.new("RGBA", (background[-1].size[0], int(100 * scale)), (0, 0, 0, 200))

	bg = background[-1].copy()

	if SkinPaths.skin_ini.general["Version"] == 1:
		y = 74
	else:
		y = 102

	imageproc.add(img, bg, 0, y * scale, topleft=True)
	imageproc.add(blackbar, bg, 0, 0, topleft=True)
	return [bg]
