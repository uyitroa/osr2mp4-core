import re

from osr2mp4.osrparse.enums import Mod


def mod_string_to_enums(mods):
	mods = mods.upper()
	mods = re.findall('..', mods)

	modnames = {
		"AT": Mod.Autoplay,
		"PF": Mod.Perfect,
		"AP": Mod.Autopilot,
		"RX": Mod.Relax,
		"SO": Mod.SpunOut,
		"FL": Mod.Flashlight,
		"HD": Mod.Hidden,
		"NC": Mod.Nightcore,
		"DT": Mod.DoubleTime,
		"SD": Mod.SuddenDeath,
		"HR": Mod.HardRock,
		"HT": Mod.HalfTime,
		"NF": Mod.NoFail,
		"EZ": Mod.Easy,
		"NM": Mod.NoMod,
}

	mod_enums = []
	for mod in mods:
		if mod in modnames:
			mod_enums.append(modnames[mod])

	return mod_enums
