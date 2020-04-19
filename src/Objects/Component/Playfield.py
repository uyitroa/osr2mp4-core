import cv2

FORMAT = ".png"


class Playfield:
	def __init__(self, filename, width, height):
		self.img = cv2.imread(filename + FORMAT, -1)
		self.img = cv2.resize(self.img, (width, height), interpolation=cv2.INTER_NEAREST)

	def add_to_frame(self, background):
		y1, y2 = 0, background.shape[0]
		x1, x2 = 0, background.shape[1]

		alpha_s = self.img[:, :, 3] / 255.0
		alpha_l = 1.0 - alpha_s

		for c in range(0, 3):
			background[y1:y2, x1:x2, c] = (alpha_s * self.img[:, :, c] + alpha_l * background[y1:y2, x1:x2, c])

