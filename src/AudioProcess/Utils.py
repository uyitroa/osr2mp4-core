def overlay(time, song, hitsound, volume=1):
	index = int(time / 1000 * song.rate)
	song.audio[index:index + len(hitsound.audio)] += hitsound.audio * 0.5 * volume
