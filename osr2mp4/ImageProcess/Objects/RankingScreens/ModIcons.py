from PIL import Image

from ....global_var import sortedmods
from ....osrparse.enums import Mod

from ... import imageproc
from .ARankingScreen import ARankingScreen


class ModIcons(ARankingScreen):
	def __init__(self, frames, replayinfo, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings=settings)
		self.mods = replayinfo.mod_combination
		self.modframes = frames

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:

			x = 1300 * self.settings.scale
			step_x = 60 * self.settings.scale
			hasnc = Mod.Nightcore in self.mods
			for mod in sortedmods:
				# if there is nightcore, then doubletime mod is present in the frozenset
				if mod == Mod.DoubleTime and hasnc:
					return

				if mod in self.mods:
					imageproc.add(self.modframes[mod], background, x, 420 * self.settings.scale, self.alpha)
					x -= step_x
