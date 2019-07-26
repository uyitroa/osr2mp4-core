from Objects.abstracts import *



spinnercircle = "spinner-circle.png"
spinnerbackground = "spinner-background.png"
spinnerbottom = "spinner-bottom.png"
spinnerspin = "spinner-spin.png"
spinnermetre = "spinner-metre.png"
spinnerapproachcircle = "spinner-approachcircle.png"
spinnertop = "spinner-top.png"


class PrepareSpinner(Images):
	def __init__(self, od, scale, path):
		self.divide_by_255 = 1/255.0
		self.scale = scale * 1.3 * 0.5
		self.path = path
		self.spinners = []
		self.spinner_frames = []
		self.spinner_images = {}
		self.interval = 1000/60
		self.diff_multiplier = self.diffrange(od, 3, 5, 7.5)
		self.load_spinner()
		print("done loading spinner")
		self.prepare_spinner()
		print("done prepraing spinner")

	def load_spinner(self):
		n = [spinnercircle, spinnerbackground, spinnerbottom, spinnerspin, spinnermetre, spinnerapproachcircle, spinnertop]
		for img in n:
			self.spinner_images[img] = Images(self.path + img, self.scale)

		max_width = 0
		max_height = 0
		for name in self.spinner_images:
			img = self.spinner_images[name].img
			if img.shape[0] > max_height:
				max_height = img.shape[0]
			if img.shape[1] > max_width:
				max_width = img.shape[1]
		self.blank = np.zeros((max_height, max_width, 4))
		self.spinner_images[spinnerbackground].add_to_frame(self.blank, int(max_width/2), int(max_height/2), 4)

	def to_frame(self, bg, img):
		y1, y2 = int(bg.shape[0]/2 - img.shape[0]/2), int(bg.shape[0]/2 + img.shape[0]/2)
		x1, x2 = int(bg.shape[1]/2 - img.shape[1]/2), int(bg.shape[1]/2 + img.shape[1]/2)

		alpha_s = img[:, :, 3] * self.divide_by_255
		alpha_l = 1 - alpha_s

		for c in range(3):
			bg[y1:y2, x1:x2, c] = img[:, :, c] * alpha_s + \
			                              alpha_l * bg[y1:y2, x1:x2, c]
		bg[y1:y2, x1:x2, 3] = bg[y1:y2, x1:x2, 3] * alpha_l + alpha_s * img[:, :, 3]

	def prepare_spinner(self):
		self.spinner_images[spinnercircle].to_3channel()
		for x in range(10, -1, -1):
			height, width, a = self.spinner_images[spinnermetre].img.shape
			height = int(height * x/10)
			partial_metre = np.copy(self.spinner_images[spinnermetre].img)
			partial_metre[:height, :, :] = np.zeros((height, width, 4))[:, :, :]

			new_img = np.copy(self.blank)
			self.to_frame(new_img, partial_metre)
			#self.to_frame(new_img, self.spinner_images[spinnerbottom].img)
			self.orig_img = new_img
			self.to_3channel()
			self.spinner_frames.append(self.orig_img)


	def add_spinner(self, starttime, endtime, curtime):
		duration = endtime - starttime
		spinrequired = int(duration * self.diff_multiplier * 0.6 / 1000)
		spinrequired = max(1, spinrequired)
		self.spinners.append([spinrequired, duration, starttime - curtime, 0])

	def diffrange(self, diff, mini, mid, maxi):
		if diff > 5:
			return mid + (maxi - mid) * (diff - 5) / 5
		if diff < 5:
			return mid - (mid - mini) * (5 - diff) / 5
		return mid

	def add_to_frame(self, background, i):
		if self.spinners[i][2] > 0:
			self.spinners[i][2] -= self.interval
			self.spinners[i][3] = min(1, self.spinners[i][3] + self.interval / 400)
		else:
			self.spinners[i][1] -= self.interval
			self.spinners[i][3] = 100

		if 0 > self.spinners[i][1] > -200:
			self.spinners[i][2] = max(0, self.spinners[i][2] - self.interval / 200)

		self.img = self.spinner_frames[10][:, :, :] * self.spinners[i][2]
		super().add_to_frame(background, int(background.shape[1] / 2), int(background.shape[0] / 2))
		self.img = self.spinner_images[spinnercircle].img[:, :, :] * self.spinners[i][2]
		super().add_to_frame(background, int(background.shape[1]/2), int(background.shape[0]/2))
