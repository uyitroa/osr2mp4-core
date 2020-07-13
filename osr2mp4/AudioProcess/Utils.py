from .Hitsound import Hitsound
from ..EEnum.EAudio import Sound


def overlay(time, song, hitsound, volume=1.0):
	index = int(time / 1000 * song.rate)
	endindex = min(index + len(hitsound.audio), len(song.audio))
	song.audio[index:endindex] += hitsound.audio[:endindex - index] * 0.5 * volume


def overlays(time, song, sounds, volume=1.0):
	overlay(time, song, Hitsound.hitsounds[sounds[0]], volume=volume)
	for f in sounds[1:]:
		overlay(time, song, Hitsound.hitsounds[f], volume=volume * 0.5)


def getcirclehitsound(n):
	whistle = n & 2 == 2
	finish = n & 4 == 4
	clap = n & 8 == 8
	normal = False  #  not (whistle or finish or clap)
	return normal, whistle, finish, clap


def getsliderhitsound(n):
	whistle = n & 2 == 2
	slide = not whistle
	return slide, whistle


def gethitsounds(n, objtype):
	n = int(n)
	if objtype == "circle":
		return getcirclehitsound(n)
	else:
		return getsliderhitsound(n)


def getfilename(timing, soundinfo, sampleset, hitsound, hitsoundset, objtype):
	hitsound_names = []
	objname = {"circle": "hit", "slider": "slider"}
	for key, i in enumerate(gethitsounds(hitsound, objtype)):
		if i:
			hitsound_names.append(hitsoundset[str(key)])

	index_name = "0"
	if len(soundinfo) > Sound.index:
		index_name = soundinfo[Sound.index]
	if index_name == "0":
		index_name = timing["SampleIndex"]

	if soundinfo[Sound.normalset] != "0":
		samplekey = soundinfo[Sound.normalset]
	else:
		samplekey = timing["SampleSet"]

	# samplekey = str(int(samplekey) % len(sampleset))  # in case out of range
	sample_name = sampleset[samplekey]

	additional_name = sampleset[soundinfo[Sound.additionalset]]
	if objtype == "slider" or soundinfo[Sound.additionalset] == "0":
		additional_name = sample_name

	filenames = []
	if len(soundinfo) > 4 and soundinfo[Sound.filename] != '':
		filenames = [soundinfo[Sound.filename]]
	else:
		filenames.append(sample_name + "-" + objname[objtype] + "normal")
		if index_name != "0" and index_name != "1":
			filenames[-1] += index_name
		for x in range(len(hitsound_names)):
			if objtype == "circle":
				filenames.append(additional_name + "-" + objname[objtype] + hitsound_names[x])
				if index_name != "0" and index_name != "1":
					filenames[-1] += index_name
	return filenames


def addfilename(beatmapsound, skinsound, soundinfo, timing, filenames, hitobjects, key):
	hitobjects[key] = []
	for i in filenames:
		index_name = "0"
		if len(soundinfo) > Sound.index:
			index_name = soundinfo[Sound.index]
		if index_name == "0":
			index_name = timing["SampleIndex"]

		if index_name == "0":
			skinsound[i] = None
		else:
			beatmapsound[i] = None
		hitobjects[key].append(i)


def getfilenames(beatmap, ignore):
	# also change hitsample and edgesample of beatmap

	timingpoint_i = 0
	beatmapsound = {}
	skinsound = {}
	hitsoundset = {"0": "normal", "1": "whistle", "2": "finish", "3": "clap"}
	sliderset = {"0": "slide", "1": "whilstle"}
	sampleset = {"0": "normal", "1": "normal", "2": "soft", "3": "drum"}

	for i in range(len(beatmap.hitobjects)-1):
		my_dict = beatmap.hitobjects[i]
		if "spinner" in my_dict["type"]:
			continue

		# use next off_set or not
		while my_dict["time"] >= beatmap.timing_point[timingpoint_i + 1]["Offset"]-1:
			timingpoint_i += 1
		soundinfo = my_dict["hitSample"].split(":")
		if len(soundinfo) < 4:
			soundinfo += (4 - len(soundinfo)) * ["0"]

		hitsound = my_dict["hitSound"]

		if "slider" in my_dict["type"]:
			sampleset_name = sampleset[beatmap.timing_point[timingpoint_i]["SampleSet"]]


		my_dict["hitSample"] = soundinfo
		if ignore:
			my_dict["soundcircle"] = ["normal-hitnormal"]
			if "slider" in my_dict["type"]:
				my_dict["soundhead"] = ["normal-hitnormal"]
				for arrowi in range(1, my_dict["repeated"]):
					my_dict["soundarrow{}".format(arrowi)] =  ["normal-hitnormal"]
				my_dict["soundtick"] = ["normal-slidertick"]
				my_dict["soundend"] = ["normal-hitnormal"]
			continue


		objtype = "circle"
		soundset = hitsoundset
		if "slider" in my_dict["type"]:
			soundset = sliderset
			objtype = "slider"

			slidersoundinfo = my_dict["edgeSets"].split("|")
			slidersoundinfo[0] = slidersoundinfo[0].split(":")
			slidersoundinfo[-1] = slidersoundinfo[-1].split(":")

			sliderhitsound = my_dict["edgeSounds"].split("|")


			f = getfilename(beatmap.timing_point[timingpoint_i], slidersoundinfo[0], sampleset, sliderhitsound[0], hitsoundset, "circle")
			addfilename(beatmapsound, skinsound, slidersoundinfo[0], beatmap.timing_point[timingpoint_i], f, my_dict, "soundhead")

			for ii in range(1, len(slidersoundinfo)-1):
				slidersoundinfo[ii] = slidersoundinfo[ii].split(":")
				end_index = timingpoint_i
				while my_dict["time"] + my_dict["duration"] * ii >= beatmap.timing_point[end_index + 1]["Offset"]-1:
					end_index += 1
				f = getfilename(beatmap.timing_point[end_index], slidersoundinfo[ii], sampleset, sliderhitsound[ii], hitsoundset, "circle")
				addfilename(beatmapsound, skinsound, slidersoundinfo[ii], beatmap.timing_point[end_index], f, my_dict, "soundarrow{}".format(str(ii)))


			end_index = timingpoint_i
			while my_dict["end time"] >= beatmap.timing_point[end_index + 1]["Offset"]-1:
				end_index += 1
			f = getfilename(beatmap.timing_point[end_index], slidersoundinfo[-1], sampleset, sliderhitsound[-1], hitsoundset, "circle")
			addfilename(beatmapsound, skinsound, slidersoundinfo[-1], beatmap.timing_point[end_index], f, my_dict, "soundend")

			slidertickname = [sampleset[soundinfo[Sound.normalset]] + "-slidertick"]
			addfilename(beatmapsound, skinsound, soundinfo, beatmap.timing_point[timingpoint_i], slidertickname, my_dict, "soundtick")

			my_dict["edgeSets"] = slidersoundinfo
			my_dict["edgeSounds"] = sliderhitsound

		f = getfilename(beatmap.timing_point[timingpoint_i], soundinfo, sampleset, hitsound, soundset, objtype)
		addfilename(beatmapsound, skinsound, soundinfo, beatmap.timing_point[timingpoint_i], f, my_dict, "sound" + objtype)

	if ignore:
		beatmapsound = ["normal-hitnormal", "normal-slidertick"]

	return beatmapsound, skinsound


def nextpowerof2(n):
	n -= 1
	n |= n >> 1
	n |= n >> 2
	n |= n >> 4
	n |= n >> 8
	n |= n >> 16
	n += 1
	return n
