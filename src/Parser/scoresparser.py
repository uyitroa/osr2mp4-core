from struct import unpack_from


def parseNum(db, offset, length):
	typeMap = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}
	numType = typeMap[length]
	val = unpack_from(numType, db, offset)[0]
	return (val, offset + length)


def parseDate(db, offset):
	val = unpack_from('Q', db, offset)[0]
	return ((val / 10000) - 62135769600000, offset + 8)


def parseFloat(db, offset, length):
	typeMap = {4: 'f', 8: 'd'}
	numType = typeMap[length]
	val = unpack_from(numType, db, offset)[0]
	return (val, offset + length)


def parseBool(db, offset):
	val = unpack_from('b', db, offset)[0]
	if val == 0x00:
		return (False, offset + 1)
	else:
		return (True, offset + 1)


def parseString(db, offset):
	existence = unpack_from('b', db, offset)[0]
	if existence == 0x00:
		return ("", offset + 1)
	elif existence == 0x0b:
		# decode ULEB128
		length = 0
		shift = 0
		offset += 1
		while True:
			val = unpack_from('B', db, offset)[0]
			length |= ((val & 0x7F) << shift)
			offset += 1
			if (val & (1 << 7)) == 0:
				break
			shift += 7

		string = unpack_from(str(length) + 's', db, offset)[0]
		offset += length

		unic = u''
		try:
			unic = str(string, 'utf-8')
		except UnicodeDecodeError:
			print("Could not parse UTF-8 string, returning empty string.")

		return (unic, offset)


def parseCollectionsDb(db):
	data = {}
	offset = 0
	data['version'], offset = parseNum(db, offset, 4)
	data['num_collections'], offset = parseNum(db, offset, 4)
	data['collections'] = {}

	for i in range(0, data['num_collections']):
		name, offset = parseString(db, offset)
		num_beatmaps, offset = parseNum(db, offset, 4)
		beatmaps = []
		for j in range(0, num_beatmaps):
			md5, offset = parseString(db, offset)
			beatmaps.append(md5)

		data['collections'][name] = beatmaps

	return data


# db: string containing scores.db information
# return: scores object containing jsonnable info from db
def parseScoresDb(db):
	scores = {}
	offset = 0
	scores['version'], offset = parseNum(db, offset, 4)
	scores['num_beatmaps'], offset = parseNum(db, offset, 4)
	scores['beatmaps'] = {}

	for i in range(0, scores['num_beatmaps']):
		beatmap, offset = parseBeatmap(db, offset)
		scores['beatmaps'][beatmap["file_md5"]] = beatmap

	return scores


# db: string containing scores.db information
# offset: byte offset from where to start reading
# return: tuple (beatmap, offset) where beatmap is a jsonnable
#           object, and offset is the offset after this beatmap
def parseBeatmap(db, offset):
	beatmap = {}
	beatmap['file_md5'], offset = parseString(db, offset)
	beatmap['num_scores'], offset = parseNum(db, offset, 4)
	beatmap['scores'] = []

	for i in range(0, beatmap['num_scores']):
		score, offset = parseScore(db, offset)
		beatmap['scores'].append(score)

	beatmap['scores'] = sorted(beatmap['scores'], key=lambda s: -s['score'])

	return (beatmap, offset)


def parseLongBeatmap(db, offset):
	beatmap = {}
	beatmap['artist_name'], offset = parseString(db, offset)
	beatmap['artist_uname'], offset = parseString(db, offset)
	beatmap['song_title'], offset = parseString(db, offset)
	beatmap['song_utitle'], offset = parseString(db, offset)
	beatmap['creator_name'], offset = parseString(db, offset)
	beatmap['version'], offset = parseString(db, offset)
	beatmap['audio_file'], offset = parseString(db, offset)
	beatmap['file_md5'], offset = parseString(db, offset)
	beatmap['osu_file'], offset = parseString(db, offset)
	beatmap['ranked'], offset = parseNum(db, offset, 1)
	beatmap['num_hitcircles'], offset = parseNum(db, offset, 2)
	beatmap['num_sliders'], offset = parseNum(db, offset, 2)
	beatmap['num_spinners'], offset = parseNum(db, offset, 2)
	beatmap['last_modified'], offset = parseDate(db, offset)
	beatmap['diff_approach'], offset = parseFloat(db, offset, 4)
	beatmap['diff_size'], offset = parseFloat(db, offset, 4)
	beatmap['diff_drain'], offset = parseFloat(db, offset, 4)
	beatmap['diff_overall'], offset = parseFloat(db, offset, 4)
	beatmap['slider_velocity'], offset = parseFloat(db, offset, 8)

	difficulties = []
	# pre-computed difficulties for various mod combinations
	for i in range(0, 4):
		numPairs, offset = parseNum(db, offset, 4)
		if numPairs == 0:
			difficulties.append(0.0)
		for j in range(0, numPairs):
			aByte, offset = parseNum(db, offset, 1)
			theInt, offset = parseNum(db, offset, 4)
			aByte, offset = parseNum(db, offset, 1)
			theDouble, offset = parseFloat(db, offset, 8)
			# print str(theInt) + ' ' + str(theDouble)
			if j == 0:
				difficulties.append(theDouble)

	beatmap['hit_length'], offset = parseNum(db, offset, 4)
	beatmap['total_length'], offset = parseNum(db, offset, 4)
	beatmap['preview_point'], offset = parseNum(db, offset, 4)

	numPoints, offset = parseNum(db, offset, 4)
	beatmap['timing_points'] = []
	for i in range(0, numPoints):
		tp, offset = parseTimingPoint(db, offset)
		beatmap['timing_points'].append(tp)

	beatmap['beatmap_id'], offset = parseNum(db, offset, 4)
	beatmap['set_id'], offset = parseNum(db, offset, 4)
	beatmap['thread_id'], offset = parseNum(db, offset, 4)

	# 4 unknown bytes
	something, offset = parseNum(db, offset, 4)

	beatmap['local_offset'], offset = parseNum(db, offset, 2)
	beatmap['stack_leniency'], offset = parseFloat(db, offset, 4)
	beatmap['mode'], offset = parseNum(db, offset, 1)
	beatmap['source'], offset = parseString(db, offset)
	beatmap['tags'], offset = parseString(db, offset)
	beatmap['online_offset'], offset = parseNum(db, offset, 2)
	beatmap['title_font'], offset = parseString(db, offset)
	beatmap['unplayed'], offset = parseBool(db, offset)
	beatmap['last_played'], offset = parseDate(db, offset)
	beatmap['is_osz2'], offset = parseBool(db, offset)
	beatmap['folder_name'], offset = parseString(db, offset)
	beatmap['last_checked'], offset = parseDate(db, offset)
	beatmap['ignore_sounds'], offset = parseBool(db, offset)
	beatmap['ignore_skin'], offset = parseBool(db, offset)
	beatmap['disable_storyboard'], offset = parseBool(db, offset)
	beatmap['disable_video'], offset = parseBool(db, offset)
	beatmap['visual_override'], offset = parseBool(db, offset)
	beatmap['last_modified'], offset = parseNum(db, offset, 4)
	beatmap['scroll_speed'], offset = parseNum(db, offset, 1)

	# extra metadata
	bpms = [p['bpm'] for p in beatmap['timing_points'] if not p['inherited']]
	beatmap['max_bpm'] = max(bpms)
	beatmap['min_bpm'] = min(bpms)
	beatmap['bpm'] = beatmap['timing_points'][0]['bpm']
	beatmap['difficultyrating'] = difficulties[beatmap['mode']]
	beatmap['num_objects'] = beatmap['num_hitcircles'] + beatmap['num_sliders'] + beatmap['num_spinners']

	return (beatmap, offset)


def parseTimingPoint(db, offset):
	tp = {}
	mpb, offset = parseFloat(db, offset, 8)
	tp['bpm'] = round(1.0 / mpb * 1000 * 60, 3)
	tp['offset'], offset = parseFloat(db, offset, 8)
	tp['inherited'], offset = parseBool(db, offset)

	tp['inherited'] = not tp['inherited']

	return (tp, offset)


def parseScore(db, offset):
	score = {}
	score['mode'], offset = parseNum(db, offset, 1)
	score['version'], offset = parseNum(db, offset, 4)
	score['md5'], offset = parseString(db, offset)
	score['player'], offset = parseString(db, offset)
	score['replay_md5'], offset = parseString(db, offset)
	score['num_300'], offset = parseNum(db, offset, 2)
	score['num_100'], offset = parseNum(db, offset, 2)
	score['num_50'], offset = parseNum(db, offset, 2)
	score['num_geki'], offset = parseNum(db, offset, 2)
	score['num_katu'], offset = parseNum(db, offset, 2)
	score['num_miss'], offset = parseNum(db, offset, 2)
	score['score'], offset = parseNum(db, offset, 4)
	score['max_combo'], offset = parseNum(db, offset, 2)
	score['perfect_combo'], offset = parseBool(db, offset)
	modFlags, offset = parseNum(db, offset, 4)
	score['mods'] = parseMods(modFlags)
	empty, offset = parseString(db, offset)
	score['timestamp'], offset = parseDate(db, offset)
	fff, offset = parseNum(db, offset, 4)
	score['score_id'], offset = parseNum(db, offset, 8)

	# no mod flag
	if not any(score['mods'].values()):
		score['mods']['no_mod'] = True
	else:
		score['mods']['no_mod'] = False

	# accuracy calculation
	misses = score['num_miss']
	num300 = score['num_300']
	num100 = score['num_100']
	num50 = score['num_50']
	numGeki = score['num_geki']
	numKatu = score['num_katu']

	# osu!std
	if score['mode'] == 0:
		numNotes = misses + num300 + num100 + num50
		weightedScore = num300 + num100 * 2.0 / 6.0 + num50 * 1.0 / 6.0
		score['accuracy'] = weightedScore / numNotes

		if score['accuracy'] == 1.0:
			score['grade'] = 'SS'
		elif float(num300) / numNotes >= 0.9 \
				and float(num50) / numNotes <= 0.1 \
				and misses == 0:
			score['grade'] = 'S'
		elif float(num300) / numNotes >= 0.8 and misses == 0 \
				or float(num300) / numNotes >= 0.9:
			score['grade'] = 'A'
		elif float(num300) / numNotes >= 0.7 and misses == 0 \
				or float(num300) / numNotes >= 0.8:
			score['grade'] = 'B'
		elif float(num300) / numNotes >= 0.6:
			score['grade'] = 'C'
		else:
			score['grade'] = 'D'

	# taiko
	elif score['mode'] == 1:
		numNotes = misses + num300 + num100
		weightedScore = num300 + num100 * 0.5
		score['accuracy'] = weightedScore / numNotes

		if score['accuracy'] == 1.0:
			score['grade'] = 'SS'
		elif float(num300) / numNotes >= 0.9 \
				and misses == 0:
			score['grade'] = 'S'
		elif float(num300) / numNotes >= 0.8 and misses == 0 \
				or float(num300) / numNotes >= 0.9:
			score['grade'] = 'A'
		elif float(num300) / numNotes >= 0.7 and misses == 0 \
				or float(num300) / numNotes >= 0.8:
			score['grade'] = 'B'
		elif float(num300) / numNotes >= 0.6:
			score['grade'] = 'C'
		else:
			score['grade'] = 'D'

	# catch the beat
	elif score['mode'] == 2:
		numNotes = num300 + num100 + num50 + misses + numKatu
		weightedScore = num300 + num100 + num50
		score['accuracy'] = float(weightedScore) / numNotes

		if score['accuracy'] == 1.0:
			score['grade'] = 'SS'
		elif score['accuracy'] > .98:
			score['grade'] = 'S'
		elif score['accuracy'] > .94:
			score['grade'] = 'A'
		elif score['accuracy'] > .90:
			score['grade'] = 'B'
		elif score['accuracy'] > .85:
			score['grade'] = 'C'
		else:
			score['grade'] = 'D'

	# osu mania
	elif score['mode'] == 3:
		numNotes = numGeki + num300 + numKatu + num100 + num50 + misses
		weightedScore = numGeki + num300 + numKatu * 2.0 / 3.0 \
		                + num100 * 1.0 / 3.0 + num50 * 1.0 / 6.0
		score['accuracy'] = weightedScore / numNotes

		if score['accuracy'] == 1.0:
			score['grade'] = 'SS'
		elif score['accuracy'] > .95:
			score['grade'] = 'S'
		elif score['accuracy'] > .90:
			score['grade'] = 'A'
		elif score['accuracy'] > .80:
			score['grade'] = 'B'
		elif score['accuracy'] > .70:
			score['grade'] = 'C'
		else:
			score['grade'] = 'D'

	return score, offset


def parseMods(modFlags):
	mods = ['no_fail', 'easy', 'no_video', 'hidden', 'hard_rock', 'sudden_death', 'double_time', 'relax', 'half_time', 'nightcore',
	        'flashlight', 'autoplay', 'spun_out', 'auto_pilot', 'perfect', 'key4', 'key5', 'key6', 'key7', 'key8', 'fade_in', 'random',
	        'cinema', 'target_practice', 'key9', 'coop', 'key1', 'key3', 'key2']

	modObject = {}
	for i, mod in enumerate(mods):
		if (modFlags & (1 << i)) != 0:
			modObject[mod] = True
		else:
			modObject[mod] = False
	modObject["modFlags"] = modFlags
	return modObject


# parses the osu!.db file
def parseOsuDb(db):
	offset = 0
	data = {}
	data['version'], offset = parseNum(db, offset, 4)
	data['folder_count'], offset = parseNum(db, offset, 4)
	data['account_unlocked'], offset = parseBool(db, offset)
	# yo i'm not sure about this
	data['unlock_date'], offset = parseNum(db, offset, 8)
	data['name'], offset = parseString(db, offset)
	data['num_beatmaps'], offset = parseNum(db, offset, 4)

	data['beatmaps'] = {}
	for i in range(0, data['num_beatmaps']):
		beatmap, offset = parseLongBeatmap(db, offset)
		data['beatmaps'][beatmap['file_md5']] = beatmap

	return data


def getscores(beatmaphash, dbpath):
	# load the scores.db file in this directory
	scoresDb = open(dbpath, "rb")
	scores = parseScoresDb(scoresDb.read())
	scoresDb.close()

	score = scores["beatmaps"].get(beatmaphash, {"num_scores": 0, "scores": []})
	return score
