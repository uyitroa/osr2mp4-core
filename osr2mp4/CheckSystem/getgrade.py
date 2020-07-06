from ..EEnum.EGrade import Grade


def getgrade(acc):
	grades = {10: Grade.SS, 9: Grade.S, 8: Grade.A, 7: Grade.B, 6: Grade.C, 5: Grade.D}

	total = acc[300] + acc[100] + acc[50] + acc[0]
	p300 = acc[300] / total
	playergrade = max(5, int(p300 * 10)) - int(acc[0] > 0)
	playergrade = max(5, playergrade)

	# Over 90% 300s, less than 1% 50s and no misses
	p50 = acc[50] / total
	playergrade -= int(playergrade == 9 and p50 >= 0.01)
	return grades[playergrade]
