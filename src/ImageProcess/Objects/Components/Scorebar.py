from CheckSystem.Health import HealthProcessor
from ImageProcess import imageproc
from ImageProcess.PrepareFrames.Components.AScorebar import AScorebar
from global_var import Settings


class Scorebar(AScorebar):
	def __init__(self, frames, beatmap):
		AScorebar.__init__(self, frames)
		self.healthprocessor = HealthProcessor(beatmap, beatmap.health_processor.drain_rate)
		self.lasttime = None
		self.endtime = None
		self.hp = 1
		self.step = 0

		self.x = 5 * Settings.scale
		self.y = 16 * Settings.scale

	def startbreak(self, breakk, duration):
		self.endtime = breakk["End"]
		AScorebar.startbreak(self, breakk, duration)

	def set_hp(self, hp):
		self.healthprocessor.health_value = hp
		self.hp = hp

	def to_hp(self, hp):
		self.healthprocessor.health_value = hp
		self.step = (hp - self.hp)/5

	def updatehp(self, hitresult, objtype):
		self.healthprocessor.updatehp(hitresult, objtype)

	def drainhp(self, cur_time):
		if self.lasttime is None:
			self.lasttime = cur_time
		in_break = self.breakk is not None and self.breakk <= cur_time <= self.endtime
		self.healthprocessor.drainhp(cur_time, self.lasttime, in_break)
		self.lasttime = cur_time

	def add_to_frame(self, background, cur_time):
		AScorebar.animate(self)

		self.frame_index += 60/Settings.fps
		self.frame_index = int(self.frame_index % len(self.frames))

		self.drainhp(cur_time)

		img = self.frames[self.frame_index]
		img = img.crop((0, 0, int(img.size[0] * self.healthprocessor.health_value), img.size[1]))
		imageproc.add(img, background, self.x, self.y-self.h, alpha=self.alpha, topleft=True)
