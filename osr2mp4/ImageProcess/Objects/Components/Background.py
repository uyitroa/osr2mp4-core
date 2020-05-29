from ... import imageproc
from ..FrameObject import FrameObject
from ....global_var import Settings, GameplaySettings


class Background(FrameObject):
	def __init__(self, bg, start_time):
		super().__init__(bg)
		self.start_time = 0
		self.map_start = start_time
		self.starting = False
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

	def add_to_frame(self, background, np, cur_time, inbreak):

		if cur_time <= self.map_start:
			i = max(0, min(1, (self.map_start - cur_time)/1000))
			self.frame_index = round(i * len(self.frames) - 1)
			self.starting = True
		elif self.starting:
			self.frame_index = 0
			self.starting = False

		self.frame_index = max(0, min(len(self.frames) - 1, self.frame_index + self.step))

		if self.start_time < cur_time < self.end_time:
			self.step = self.interval * 60/Settings.fps
		if (cur_time > self.end_time - 500 and int(self.frame_index) >= len(self.frames) - 1) or self.fadeout:
			self.fadeout = True
			self.step = -self.interval * 60/Settings.fps

		if int(self.frame_index) <= 0:
			if inbreak or cur_time < self.map_start or not GameplaySettings.settings["In-game interface"]:
				if GameplaySettings.settings["Background dim"] == 100:
					np.fill(0)
				else:
					# imageproc.add(self.frames[1], background, Settings.width//2, Settings.height//2)
					background.paste(self.frames[1], (0, 0))
			return

		super().add_to_frame(background, Settings.width//2, Settings.height//2)
