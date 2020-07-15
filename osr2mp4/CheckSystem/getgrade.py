from ..EEnum.EGrade import Grade


def getgrade(acc):
	total = acc[300] + acc[100] + acc[50] + acc[0]
	p300 = acc[300] / total
	p50 = acc[50] / total
	if p300 == 1.0:
		return Grade.SS
	elif p300 > 0.9 and p50 < 0.01 and acc[0] == 0:
		return Grade.S
	elif (p300 > 0.9 and acc[0] > 0) or (p300 > 0.8 and acc[0] == 0):
		return Grade.A
	elif (p300 > 0.7 and acc[0] == 0) or (p300 > 0.8 and acc[0] > 0):
		return Grade.B
	elif p300 > 0.6:
		return Grade.C

	return Grade.D
