import cv2
from PIL import Image, ImageDraw


def changealpha(img, alpha):
	"""
	Directly change the current image without returning
	:param img: PIL.Image
	:param alpha: float
	:return:
	"""
	a = img.getchannel('A')
	a = a.point(lambda i: i * alpha)
	img.putalpha(a)


def addalpha(img, alpha):
	a = img.getchannel('A')
	a = a.point(lambda i: i + alpha)
	img.putalpha(a)


def newalpha(img, alpha):
	"""
	Multiplication of image alpha channel and alpha
	:param img: PIL.Image
	:param alpha: float
	:return: PIL.Image
	"""
	out = img.copy()
	a = img.getchannel('A')
	a = a.point(lambda i: i * alpha)
	out.putalpha(a)
	return out


def add_color(image, color):
	"""
	Multiplication of color/255 with image color channel
	:param image:  PIL.Image
	:param color: tuple RG
	:return: PIL.Image
	"""
	im = image.copy()
	r, g, b, a = im.split()
	r = r.point(lambda i: i * color[0] / 255)
	g = g.point(lambda i: i * color[1] / 255)
	b = b.point(lambda i: i * color[2] / 255)
	out = Image.merge('RGBA', (r, g, b, a))
	return out


def add_color_s(imglist, color):
	new = []
	for img in imglist:
		new.append(add_color(img, color))
	return new


def add(img, background, x_offset, y_offset, alpha=1, channel=3, topleft=False):
	"""
	Add image to the background
	:param img: PIL.Image
	:param background: PIL.Image
	:param x_offset: int
	:param y_offset: int
	:param alpha: float between 0 and 1
	:return:
	"""
	if img.size[0] == 1 and img.size[1] == 1:
		return
	if img.size[0] == 0 or img.size[1] == 0:
		return

	if background.size[0] == 0 or background.size[1] == 0:
		return

	if not topleft:
		y_offset = y_offset - img.size[1]/2
		x_offset = x_offset - img.size[0]/2

	x_offset, y_offset = round(x_offset), round(y_offset)
	alpha = max(0, min(alpha, 1))

	if channel == 3:

		a = img
		if 0 < alpha < 1:
			a = img.getchannel("A")
			a = a.point(lambda i: i * alpha)
		if alpha <= 0:
			return
		background.paste(img, (x_offset, y_offset), a)

	elif channel == 4:

		img2 = img.copy()
		if 0 < alpha < 1:
			a = img.getchannel("A")
			a = a.point(lambda i: i * alpha)
			img2.putalpha(a)
		if alpha <= 0:
			return
		b = background.crop((x_offset, y_offset, x_offset + img.size[0], y_offset + img.size[1]))
		c = Image.alpha_composite(b, img2)
		background.paste(c, (x_offset, y_offset))


def change_size(img, scale_row, scale_col, rows=None, cols=None):
	"""
	:param img: PIL.Image
	:param scale_row: float
	:param scale_col: float
	:param rows: int
	:param cols: int
	:return: PIL.Image
	"""
	if rows is None:
		rows = img.size[1]
		cols = img.size[0]
	n_rows = max(2, int(scale_row * rows))
	n_rows += int(n_rows % 2 == 1)  # need to be even
	n_cols = max(2, int(scale_col * cols))
	n_cols += int(n_cols % 2 == 1)  # need to be even

	return img.resize((n_cols, n_rows), Image.ANTIALIAS)


def change_sizes(imglist, scale_row, scale_col, rows=None, cols=None):
	news = []
	for img in imglist:
		news.append(change_size(img, scale_row, scale_col, rows=rows, cols=cols))
	return news


def rotate_images(frames, angle):
	images = [None] * len(frames)
	for x in range(len(frames)):
		images[x] = frames[x].rotate(angle, resample=Image.BILINEAR)
	return images


def draw_number(background, number, frames, x, y, alpha, origin, gap, constantgap=False):
	
	direction = 1 if origin == "left" else -1
	scorestr = str(number) if origin == "left" else str(number)[::-1]

	if origin == 'center':
		width = sum([
					frames[int(letter) if letter.isdigit() else letter].size[0] * -1
					for letter in scorestr
					])

		x -= width / 2
		draw_number(background, number, frames, x, y, alpha, 'right', 0)
	else:
		first = True
		for n in scorestr:
			index = int(n) if n.isdigit() else n
			if not first and not constantgap:
				x += (frames[index].size[0] - gap) * direction/2
			first = False

			add(frames[index], background, x, y, alpha=alpha)

			if constantgap:
				x += (frames[0].size[0] - gap) * direction
			else:
				x += (frames[index].size[0] - gap) * direction/2
		

def get_number_size(number, frames, gap, constantgap=False):
	x = 0
	first = True
	for n in str(number):
		index = int(n) if n.isdigit() else n
		if not first and not constantgap:
			x += (frames[index].size[0] - gap)/2
		first = False

		if constantgap:
			x += (frames[0].size[0] - gap)
		else:
			x += (frames[index].size[0] - gap)/2

	return x


def debug(background, *args):
	text = ""
	pos = (100, 100)
	for t in args:
		text += str(t) + " "

	if type(background).__name__ == "Image":
		draw = ImageDraw.Draw(background)
		draw.text(pos, text, (255, 255, 255))
	else:
		font = cv2.FONT_HERSHEY_SIMPLEX
		bottomLeftCornerOfText = pos
		fontScale = 1
		fontColor = (255, 255, 255)
		lineType = 2

		cv2.putText(background, text,
					bottomLeftCornerOfText,
					font,
					fontScale,
					fontColor,
					lineType)

