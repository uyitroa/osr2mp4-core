from Objects.abstracts import *


spinnerbackground = "spinner-background.png"
spinnercircle = "spinner-circle.png"


class SpinnerManager(Images):
	def __init__(self, frames, scale):
		self.scale = scale
		self.spinners = {}
		self.spinner_images, self.spinnermetre, self.spinner_frames = frames

		self.interval = 1000/60

	def add_spinner(self, starttime, endtime, curtime):
		duration = endtime - starttime
		# img, duration, startime left, alpha, index, progress
		self.spinners[str(starttime) + "o"] = [np.copy(self.spinner_images[spinnercircle].img), duration, starttime - curtime, 0, 0]

	def update_spinner(self, timestamp, angle, progress):
		angle = round(angle)
		n_rot = int(angle/90)
		index = int(angle - 90*n_rot)

		self.spinners[timestamp][0] = np.rot90(self.spinnermetre[index], n_rot)
		progress = progress * 10
		if 0.3 < progress - int(progress) < 0.35 or 0.6 < progress - int(progress) < 0.65:
			progress -= 1

		self.spinners[timestamp][4] = min(10, int(progress))

	def add_to_frame(self, background, i):
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
		super().add_to_frame(background, background.shape[1]//2, background.shape[0]//2)

		self.img = self.spinners[i][0][:, :, :] * self.spinners[i][3]
		super().add_to_frame(background, background.shape[1]//2, background.shape[0]//2)

		self.img = self.spinner_frames[self.spinners[i][4]][:, :, :] * self.spinners[i][3]
		super().add_to_frame(background, background.shape[1]//2, int(background.shape[0]//2 - 2.5 * self.scale))  # dude idk
