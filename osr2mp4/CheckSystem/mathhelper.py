import numpy as np

from osr2mp4.osrparse.enums import Mod


def getunstablerate(resultinfo):
	error_time = []
	total = 0
	_total = 0
	count = 0
	_count = 0
	for i in resultinfo:
		if type(i.more).__name__ == "Circle" and i.hitresult is not None and i.hitresult != 0:
			error_time.append(i.more.deltat)

			if i.more.deltat >= 0:
				total += i.more.deltat
				count += 1
			else:
				_total += i.more.deltat
				_count += 1

	return 0 if _count == 0 else _total / _count, \
			0 if count == 0 else total / count, \
			np.std(error_time) * 10


def dtar(value):
	if value < 5:
		hitwindow = 1200 + 600 * (5 - value) / 5
	elif value == 5:
		hitwindow = 1200
	else:
		hitwindow = 1200 - 750 * (value - 5) / 5

	hitwindow /= 1.5

	if hitwindow > 1200:
		return round((1800 - hitwindow)/120, 2)
	else:
		return round((1200 - hitwindow)/150 + 5, 2)


def dtod(value):
	hitwindow = 50 + 30 * (5 - value) / 5 + 0.25  # it works don't ask
	hitwindow /= 1.5
	return round((80 - hitwindow)/6, 2)


def htod(value):
	hitwindow = 50 + 30 * (5 - value) / 5 - 0.125  # it works don't ask
	hitwindow /= 0.75
	return round((80 - hitwindow)/6, 2)


def htar(value):
	if value < 5:
		hitwindow = 1200 + 600 * (5 - value) / 5
	elif value == 5:
		hitwindow = 1200
	else:
		hitwindow = 1200 - 750 * (value - 5) / 5

	hitwindow /= 0.75

	if hitwindow > 1200:
		return round((1800 - hitwindow)/120, 2)
	else:
		return round((1200 - hitwindow)/150 + 5, 2)


def getar(mods, ar):
	if Mod.HardRock in mods:
		ar = min(ar * 1.4, 10)
	if Mod.Easy in mods:
		ar = ar * 0.5
	if Mod.DoubleTime in mods:
		ar = dtar(ar)
	if Mod.HalfTime in mods:
		ar = htar(ar)
	return ar


