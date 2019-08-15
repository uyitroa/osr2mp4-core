from Objects.abstracts import *


spinnerbackground = "spinner-background.png"
spinnercircle = "spinner-circle.png"


class SpinnerManager(Images):
	def __init__(self, frames, scale, moveright, movedown):
		self.moveright = moveright
		self.movedown = movedown
		self.scale = scale
		self.spinners = {}
		self.spinner_images, self.spinnermetre, self.spinner_frames = frames

		self.interval = 1000/60

	def add_spinner(self, starttime, endtime, curtime):
		duration = endtime - starttime
		# img, duration, startime left, alpha, index, progress
		self.spinners[str(starttime) + "o"] = [np.copy(self.spinner_images[spinnercircle].img), duration, starttime - curtime, 0, 0]

	def update_spinner(self, timestamp, angle, progress):
		angle = round(angle * 0.9)
		n_rot = int(angle/90)
		index = int(angle - 90*n_rot)

		self.spinners[timestamp][0] = np.rot90(self.spinnermetre[index], n_rot)
		progress = progress * 10
		if 0.3 < progress - int(progress) < 0.35 or 0.6 < progress - int(progress) < 0.65:
			progress -= 1

		self.spinners[timestamp][4] = min(10, int(progress))

	def add_to_frame(self, background, i, alone):
		if self.spinners[i][2] > 0:
			self.spinners[i][2] -= self.interval
			self.spinners[i][3] = min(1, self.spinners[i][3] + self.interval / 400)
		else:
			self.spinners[i][1] -= self.interval
			if 0 > self.spinners[i][1] > -200:
				self.spinners[i][3] = max(0, self.spinners[i][3] - self.interval / 200)
			else:
				self.spinners[i][3] = 1
		self.img = self.spinner_images[spinnerbackground].img[:, :, :] * self.spinners[i][3]
		if not alone:
			super().add_to_frame(background,  background.shape[1]//2 - 512 + self.img.shape[1]//2, 46 + self.img.shape[0]//2)
		else:
			x, y = background.shape[1]//2 - 512, 46
			y1, y2, ystart, yend = super().checkOverdisplay(y, y + self.img.shape[0], background.shape[0])
			x1, x2, xstart, xend = super().checkOverdisplay(x, x + self.img.shape[1], background.shape[1])
			background[y1:y2, x1:x2, :] = self.img[ystart:yend, xstart:xend, :3]

		self.img = self.spinners[i][0][:, :, :] * self.spinners[i][3]
		super().add_to_frame(background, background.shape[1] // 2, int(198.5 * self.scale) + self.movedown)

		self.img = self.spinner_frames[self.spinners[i][4]][:, :, :] * self.spinners[i][3]
		super().add_to_frame(background, background.shape[1]//2 - 512 + self.img.shape[1]//2, 46 + self.img.shape[0]//2)
