from PIL import Image
from ..FrameObject import FrameObject

from ....global_var import sortedmods
from ....osrparse.enums import Mod

from ... import imageproc


class PlayingModIcons(FrameObject):
	def __init__(self, frames, replayinfo, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings=settings)
		self.mods = replayinfo.mod_combination
		self.modframes = frames
		self.x = 1315 * self.settings.scale
		self.y = 130 * self.settings.scale
		self.step_x = 80 * self.settings.scale

	def add_to_frame(self, background):
		if not self.settings.settings["Show mods icon"]:
			return

		hasnc = Mod.Nightcore in self.mods
		x = self.x
		for mod in sortedmods:
			# if there is nightcore, then doubletime mod is present in the frozenset
			if mod == Mod.DoubleTime and hasnc:
				return

			if mod in self.mods:
				imageproc.add(self.modframes[mod], background, x, self.y)
				x -= self.step_x
