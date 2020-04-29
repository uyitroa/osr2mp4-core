def search_time(to_time, hitobjects):
	cur_index = 0
	while cur_index <= len(hitobjects)-1 and hitobjects[cur_index]["end time"] + 1000 < to_time:
		cur_index += 1
	return hitobjects[cur_index]["time"], cur_index


def search_updateindex(timestamp, resultinfo, component):
	cur_index = 0
	while cur_index <= len(resultinfo)-1 and resultinfo[cur_index].timestamp != timestamp:
		cur_index += 1
	info = resultinfo[max(0, cur_index-1)]
	component.scorecounter.set_score(resultinfo[cur_index].time, info.score, info.showscore)
	component.accuracy.set_acc(info.accuracy)
	component.combocounter.set_combo(info.combo)

	component.key1.set_freeze(resultinfo[cur_index].time, info.clicks[0])
	component.key2.set_freeze(resultinfo[cur_index].time, info.clicks[1])
	component.mouse1.set_freeze(resultinfo[cur_index].time, info.clicks[2])
	component.mouse2.set_freeze(resultinfo[cur_index].time, info.clicks[3])
	urindex = max(0, cur_index-1)
	diff = 0
	while diff < 3400:
		if type(resultinfo[urindex].more).__name__ == "Circle" and resultinfo[urindex].hitresult is not None:
			if resultinfo[urindex].hitresult > 0:
				component.urbar.add_bar(resultinfo[urindex].more.deltat, resultinfo[urindex].hitresult)
				pass
		urindex -= 1
		if urindex <= -1:
			break
		diff = info.time - resultinfo[urindex].time
	return cur_index


def set_scores(to_time, resultinfo, component):
	cur_index = 0
	while cur_index <= len(resultinfo)-1 and resultinfo[cur_index].time < to_time:
		cur_index += 1
	component.scorecounter.set_score(resultinfo[cur_index].score, resultinfo[cur_index].showscore)
	component.accuracy.set_acc(resultinfo[cur_index].accuracy)
	component.combocounter.set_combo(resultinfo[cur_index].combo)
	return resultinfo[cur_index].time



def search_osrindex(to_time, replays):
	# pass_counter = 0
	cur_index = 0
	while cur_index <= len(replays)-1 and replays[cur_index+1][3] < to_time:
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
		index_followpoint += 1

	index_followpoint = max(0, index_followpoint-1)
	osu_d = hitobjects[index_followpoint]
	x_end = osu_d["end x"]
	y_end = osu_d["end y"]

	return index_followpoint, object_endtime, x_end, y_end


def skip(to_time, resultinfo, replayinfo, objectinfo, timepreempt, component):
	to_time, hitobjectindex = search_time(to_time, objectinfo)
	to_time -= timepreempt
	info_index = search_updateindex(objectinfo[hitobjectindex]["time"], resultinfo, component)
	# to_time = set_scores(to_time, resultinfo, component)
	osr_index = search_osrindex(to_time, replayinfo)
	fp_index, obj_endtime, x_end, y_end = search_fpindex(to_time, objectinfo)
	return to_time, hitobjectindex, info_index, osr_index, fp_index, obj_endtime, x_end, y_end


