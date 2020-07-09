from ....osrparse.enums import Mod

from ...PrepareFrames.YImage import YImage

selectionmod = "selection-mod-"


def prepare_modicons(scale, settings):
	modnames = {
		Mod.Autoplay: "autoplay",
		Mod.Perfect: "perfect",
		Mod.Autopilot: "pilot",
		Mod.Relax: "relax",
		Mod.SpunOut: "spunout",
		Mod.Flashlight: "flashlight",
		Mod.Hidden: "hidden",
		Mod.Nightcore: "nightcore",
		Mod.DoubleTime: "doubletime",
		Mod.SuddenDeath: "suddendeath",
		Mod.HardRock: "hardrock",
		Mod.HalfTime: "halftime",
		Mod.NoFail: "nofail",
		Mod.Easy: "easy",
	}

	modframes = {}

	for mod in modnames:
		filename = selectionmod + modnames[mod]
		modframes[mod] = YImage(filename, settings, scale).img

	return modframes
