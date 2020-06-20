from PIL import Image
from osrparse.enums import Mod

from ... import imageproc
from .ARankingScreen import ARankingScreen


class ModIcons(ARankingScreen):
	def __init__(self, frames, replayinfo, settings):
		dummy = [Image.new("RGBA", (1, 1))]
		super().__init__(dummy, settings=settings)
		self.mods = replayinfo.mod_combination
		self.modframes = frames

		# source: ggjjwp
		self.sortedmods = [
			Mod.Autoplay,
			Mod.SpunOut,
			Mod.Autopilot,
			Mod.Perfect,
			Mod.Flashlight,
			Mod.DoubleTime,
			Mod.Nightcore,
			Mod.HalfTime,
			Mod.SuddenDeath,
			Mod.Relax,
			Mod.HardRock,
			Mod.Hidden,
			Mod.Easy,
			Mod.NoFail
		]

		self.sortedmods.reverse()

	def add_to_frame(self, background):
		super().add_to_frame(background)
		if self.fade == self.FADEIN:

			x = 1300 * self.settings.scale
			step_x = 60 * self.settings.scale
			for mod in self.sortedmods:
				if mod in self.mods:
					imageproc.add(self.modframes[mod], background, x, 420 * self.settings.scale, self.alpha)
					x -= step_x
