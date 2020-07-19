import numpy as np


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
