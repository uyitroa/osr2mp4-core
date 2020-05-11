def write_data(beatmap, resultinfo):
	a = open("beatmap.txt", "w")
	a.write(str(beatmap.hitobjects))
	a.close()
	a = open("resultinfo.txt", "w")
	a.write(str(resultinfo))
	a.close()

	print("\nWriting to file done\n\n")
