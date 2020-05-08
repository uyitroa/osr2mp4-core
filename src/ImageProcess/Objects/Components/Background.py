from ImageProcess.Objects.FrameObject import FrameObject
from global_var import Settings


class Background(FrameObject):
	def __init__(self, bg):
		super().__init__(bg)
		self.start_time = 0
		self.end_time = 0
		self.fade_time = 650
		self.interval = len(self.frames) / (self.fade_time * Settings.fps / 1000)
		self.step = 0
		self.fadeout = False

	def startbreak(self, event, cur_time):
		self.start_time = event["Start"]
		self.end_time = event["End"]
		self.fadeout = False

		if event["Start"] == -500:
			self.frame_index = len(self.frames) - 1

	def setalpha(self, cur_time):
		i = min(1, max(0, (cur_time - self.start_time)/self.fade_time))
		i = i * min(1, max(0, (self.end_time - cur_time)/self.fade_time))
		self.frame_index = round(i * (len(self.frames) - 1))

	def add_to_frame(self, background, np, cur_time):

		self.frame_index = max(0, min(len(self.frames) - 1, self.frame_index + self.step))

		if self.start_time < cur_time < self.end_time:
			self.step = self.interval
		if (cur_time > self.end_time - 500 and int(self.frame_index) >= len(self.frames) - 1) or self.fadeout:
			self.fadeout = True
			self.step = -self.interval

		if int(self.frame_index) <= 0:
			np.fill(0)
			return

		super().add_to_frame(background, Settings.width//2, Settings.height//2)
