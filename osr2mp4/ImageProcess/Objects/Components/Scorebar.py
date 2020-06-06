from ....CheckSystem.Health import HealthProcessor
from ... import imageproc
from .AScorebar import AScorebar


class Scorebar(AScorebar):
	def __init__(self, frames, beatmap, settings):
		AScorebar.__init__(self, frames[0], settings=settings)
		self.marker = frames[1]
		self.hasmarker = frames[2]
		self.healthprocessor = HealthProcessor(beatmap, beatmap.health_processor.drain_rate)
		self.lasttime = None
		self.endtime = None
		self.hp = 1
		self.step = 0

		if not self.hasmarker:
			self.x = 5 * self.settings.scale
			self.y = 16 * self.settings.scale
		else:
			self.x = 12 * self.settings.scale
			self.y = 12 * self.settings.scale

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

		self.frame_index += self.settings.skin_ini.general["AnimationFramerate"]/self.settings.fps
		self.frame_index = self.frame_index % len(self.frames)

		self.drainhp(cur_time)

		self.hp = max(0, min(1, self.hp + self.step))
		if self.step >= 0 and self.hp > self.healthprocessor.health_value:
			self.hp = self.healthprocessor.health_value
		elif self.step <= 0 and self.hp < self.healthprocessor.health_value:
			self.hp = self.healthprocessor.health_value

		img = self.frames[int(self.frame_index)]
		img = img.crop((0, 0, int(img.size[0] * self.hp), img.size[1]))

		if self.settings.settings["In-game interface"] or in_break:
			imageproc.add(img, background, self.x, self.y-self.h, alpha=self.alpha, topleft=True)

		if self.hasmarker:
			imageproc.add(self.marker, background, self.x + img.size[0], 16 * self.settings.scale-self.h, alpha=self.alpha)
