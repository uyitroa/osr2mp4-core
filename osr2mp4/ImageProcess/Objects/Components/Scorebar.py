from ....CheckSystem.Health import HealthProcessor
from ... import imageproc
from .AScorebar import AScorebar
from ....global_var import Settings, SkinPaths, GameplaySettings


class Scorebar(AScorebar):
	def __init__(self, frames, beatmap):
		AScorebar.__init__(self, frames[0])
		self.marker = frames[1]
		self.hasmarker = frames[2]
		self.healthprocessor = HealthProcessor(beatmap, beatmap.health_processor.drain_rate)
		self.lasttime = None
		self.endtime = None
		self.hp = 1
		self.step = 0

		if not self.hasmarker:
			self.x = 5 * Settings.scale
			self.y = 16 * Settings.scale
		else:
			self.x = 12 * Settings.scale
			self.y = 12 * Settings.scale

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
		tmp = self.healthprocessor.health_value
		self.healthprocessor.drainhp(cur_time, self.lasttime, in_break)
		self.lasttime = cur_time

		diff = self.healthprocessor.health_value - tmp
		self.hp += diff

	def add_to_frame(self, background, cur_time, in_break):

		AScorebar.animate(self)

		self.frame_index += SkinPaths.skin_ini.general["AnimationFramerate"]/Settings.fps
		self.frame_index = self.frame_index % len(self.frames)

		self.drainhp(cur_time)

		self.hp = max(0, min(1, self.hp + self.step))
		if self.step >= 0 and self.hp > self.healthprocessor.health_value:
			self.hp = self.healthprocessor.health_value
		elif self.step <= 0 and self.hp < self.healthprocessor.health_value:
			self.hp = self.healthprocessor.health_value

		img = self.frames[int(self.frame_index)]
		img = img.crop((0, 0, int(img.size[0] * self.hp), img.size[1]))

		if GameplaySettings.settings["In-game interface"] or in_break:
			imageproc.add(img, background, self.x, self.y-self.h, alpha=self.alpha, topleft=True)

		if self.hasmarker:
			imageproc.add(self.marker, background, self.x + img.size[0], 16 * Settings.scale-self.h, alpha=self.alpha)
