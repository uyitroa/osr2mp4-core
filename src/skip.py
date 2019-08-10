def search_updateindex(to_time, resultinfo):
	cur_index = 0
	while cur_index <= len(resultinfo)-1 and resultinfo[cur_index+1].time < to_time:
		cur_index += 1
	return cur_index


def search_osrindex(to_time, replays):
	# pass_counter = 0
	cur_index = 0
	while cur_index <= len(replays)-1 and replays[cur_index+1][3] <= to_time:
		cur_index += 1
	#
	# cur_index -= 3
	# min_time = abs(replays[cur_index][3] - to_time)
	# min_time_toskip = min(min_time, abs(replays[cur_index+1][3] - to_time))
	#
	# returnindex = 0
	# key_state = replays[cur_index][3]
	# for x in range(1, 4):
	# 	delta_t = abs(replays[cur_index + x][3] - to_time)
	# 	if key_state != replays[cur_index + x][2]:
	# 		if delta_t <= min_time_toskip:
	# 			return x
	# 	if delta_t < min_time:
	# 		min_time = delta_t
	# 		returnindex = x
	#
	# return returnindex
	return cur_index


def search_fpindex(to_time, hitobjects):
	object_endtime = hitobjects[0]["end time"]
	index_followpoint = 0

	while to_time + 800 >= object_endtime and index_followpoint + 2 < len(hitobjects):
		while "spinner" in hitobjects[index_followpoint+1]["type"] or "new combo" in hitobjects[index_followpoint+1]["type"]:
			index_followpoint += 1

		if "end" in hitobjects[index_followpoint+1]["type"]:
			return index_followpoint * 10, hitobjects[index_followpoint]["end time"] * 10, 0, 0

		object_endtime = hitobjects[index_followpoint]["end time"]

	index_followpoint = max(0, index_followpoint-1)
	osu_d = hitobjects[index_followpoint]
	x_end = osu_d["end x"]
	y_end = osu_d["end y"]

	return index_followpoint, object_endtime, x_end, y_end


def skip(to_time, resultinfo, replayinfo, objectinfo):
	info_index = search_updateindex(to_time, resultinfo)
	to_time = resultinfo[info_index].time
	osr_index = search_osrindex(to_time, replayinfo)
	fp_index, obj_endtime, x_end, y_end = search_fpindex(to_time, objectinfo)


