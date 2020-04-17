from Objects.abstracts import *
from skimage.transform import rotate


spinnercircle = "spinner-circle.png"
spinnerbackground = "spinner-background.png"
spinnerbottom = "spinner-bottom.png"
spinnerspin = "spinner-spin.png"
spinnermetre = "spinner-metre.png"
spinnerapproachcircle = "spinner-approachcircle.png"
spinnertop = "spinner-top.png"


class PrepareSpinner(Images):
	def __init__(self, od, scale, path):

		self.scale = scale * 1.3 * 0.5
		self.path = path
		self.spinners = {}
		self.spinner_frames = []
		self.spinnermetre = []
		self.spinner_images = {}
		self.interval = 1000/60
		self.load_spinner()
		print("done loading spinner")
		self.prepare_spinner()
		print("done prepraing spinner")

	def load_spinner(self):
		print(self.scale)
		n = [spinnercircle, spinnerbackground, spinnerbottom, spinnerspin, spinnermetre, spinnerapproachcircle, spinnertop]
		for img in n:
			self.spinner_images[img] = Images(self.path + img, self.scale)

		# self.to_square(self.spinner_images[spinnercircle])

	def prepare_spinner(self):
		#self.spinner_images[spinnercircle].to_3channel()
		#self.spinner_images[spinnerbackground].to_3channel()

		for x in range(90):
			self.spinnermetre.append(rotate(self.spinner_images[spinnercircle].img, x, preserve_range=True, order=0).astype(np.uint8))

		for x in range(10, -1, -1):
			height, width, a = self.spinner_images[spinnermetre].img.shape
			height = int(height * x/10)
			partial_metre = self.spinner_images[spinnermetre].img.copy()
			partial_metre[:height, :, :] = np.zeros((height, width, 4))[:, :, :]

			# self.to_frame(new_img, self.spinner_images[spinnerbottom].img)
			self.orig_img = partial_metre.copy()
			#self.to_3channel()
			self.spinner_frames.append(self.orig_img)


	def add_spinner(self, starttime, endtime, curtime, timestamp):
		duration = endtime - starttime
		# img, duration, startime left, alpha, index, progress
		self.spinners[timestamp] = [self.spinner_images[spinnercircle].img.copy(), duration, starttime - curtime, 0, 0]

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
		super().add_to_frame(background, background.size[1]//2, background.size[0]//2)

		self.img = self.spinners[i][0][:, :, :] * self.spinners[i][3]
		super().add_to_frame(background, background.size[1]//2, background.size[0]//2)

		self.img = self.spinner_frames[self.spinners[i][4]][:, :, :] * self.spinners[i][3]
		super().add_to_frame(background, background.size[1]//2, int(background.size[0]//2 - 2.5 * self.scale))  # dude idk
