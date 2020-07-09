from copy import copy

from ... import imageproc
from ....osrparse.enums import Mod

from ....CheckSystem.getgrade import getgrade
from ..FrameObject import FrameObject


class PlayingGrade(FrameObject):
	def __init__(self, frames, timepie, replayinfo, settings):
		super().__init__(frames, settings=settings)

		self.x = timepie.x - 40 * settings.scale
		self.y = timepie.y

		self.hd = int(Mod.Hidden in replayinfo.mod_combination)
		self.gradewait = 0
		self.breakperiod = None
		self.gradeframes = frames
		self.alpha = 0

	def startbreak(self, breakperiod):
		if breakperiod["End"] - breakperiod["Start"] < 2000:
			return
		if self.breakperiod is not None and breakperiod["End"] == self.breakperiod["End"]:
			return
		# self.gradewait = 1 * self.settings.timeframe / self.settings.fps
		self.breakperiod = copy(breakperiod)
		self.breakperiod["Start"] += 100
		self.alpha = 1
		self.frame_index = 0

	def add_to_frame(self, background, accuracy, curtime):
		if self.breakperiod is None:
			return
		if self.breakperiod["Start"] <= curtime <= self.breakperiod["End"] - 300:
			grade = getgrade(accuracy)
			gradeframes = self.gradeframes[self.hd][grade]
			self.frame_index = min(self.frame_index + 0.5, len(gradeframes) - 1)
			gradeframe = gradeframes[int(self.frame_index)]
			imageproc.add(gradeframe, background, self.x, self.y)
		elif self.breakperiod["End"] - 300 < curtime <= self.breakperiod["End"]:
			grade = getgrade(accuracy)
			gradeframe = self.gradeframes[self.hd][grade][-1]
			self.alpha -= 0.1 * 60/self.settings.fps
			imageproc.add(gradeframe, background, self.x, self.y, alpha=max(0, self.alpha))



