import math
import re

from ..Exceptions import GameModeNotSupported
from ..ImageProcess.Curves.curves import getclass


class Beatmap:
	def __init__(self, info, scale=1, colors=None, hr=False):
		self.info = info
		self.general = {"StackLeniency": 7, "Mode": 0}
		self.diff = {"CircleSize": 0, "OverallDifficulty": 0, "HPDrainRate": 0}
		self.meta = {}
		self.bg = [0, 0, "."]
		self.breakperiods = []
		self.timing_point = []
		self.hitobjects = []
		self.sliderimg = {}
		self.max_combo = {}
		self.slider_combo = {}  # array of combo that are sliders. to prepare slider frames with those combo
		self.to_stack = []
		self.scale = scale
		self.path = None

		if colors is None:
			colors = {"ComboNumber": 1}
		self.ncombo = colors["ComboNumber"]
		self.hr = hr

		self.parse_general()

		if self.general["Mode"] != 0:
			raise GameModeNotSupported()

		self.parse_meta()
		self.parse_diff()

		self.parse_event()
		self.parse_timingpoints()
		self.parse_hitobject()
		self.stack_position()

		endtime_fp = self.hitobjects[-1]["time"] + 800
		# diffcalculator = DiffCalculator(self.diff)
		# timepreempt = int(diffcalculator.ar() + 500)
		# self.breakperiods.append({"Start": -500, "End": self.start_time-timepreempt, "Arrow": True})
		self.hitobjects.append({"x": 0, "y": 0, "time": endtime_fp, "end time": endtime_fp, "combo_number": 0,
		                        "type": ["end"], "id": -1})  # to avoid index out of range

		self.health_processor = None

	def parse_general(self):
		general = self.info["General"]
		general = general.split("\n")
		for item in general:
			item = item.strip()
			if item != "":
				my_list = item.split(":")
				my_list[1] = my_list[1].strip()
				self.general[my_list[0]] = float(my_list[1]) if my_list[1].replace('.', '', 1).isdigit() else my_list[1]

	def parse_meta(self):
		general = self.info["Metadata"]
		general = general.split("\n")
		for item in general:
			item = item.strip()
			if item != "":
				my_list = item.split(":")
				my_list[1] = my_list[1].strip()
				self.meta[my_list[0]] = float(my_list[1]) if my_list[1].replace('.', '', 1).isdigit() else my_list[1]

	def parse_diff(self):
		general = self.info["Difficulty"]
		general = general.split("\n")
		for item in general:
			item = item.strip()
			if item != "":
				my_list = item.split(":")
				my_list[1] = my_list[1].strip()
				self.diff[my_list[0]] = float(my_list[1]) if my_list[1].replace('.', '', 1).isdigit() else my_list[1]
				self.diff["Base" + my_list[0]] = self.diff[my_list[0]]
		self.diff["ApproachRate"] = self.diff.get("ApproachRate", self.diff["OverallDifficulty"])
		self.diff["BaseApproachRate"] = self.diff["ApproachRate"]

	def parse_event(self):
		event = self.info["Events"].split("\n")

		for line in event:
			line = line.strip()
			if line.startswith("0"):
				self.bg = line.split(",")
				self.bg[2] = self.bg[2].replace('"', '')
			if line.startswith("2"):
				my_dict = {}
				items = line.split(",")
				my_dict["Start"] = int(items[1])
				my_dict["End"] = int(items[2])
				my_dict["Arrow"] = True
				self.breakperiods.append(my_dict)

	def parse_timingpoints(self):
		timing = self.info["TimingPoints"]
		timing = timing.split("\n")
		inherited = 0
		for line in timing:
			line = line.strip()
			if line == '':
				continue
			my_dict = {}
			items = line.split(",")
			my_dict["Offset"] = float(items[0])
			if len(items) < 7 or int(items[6]) == 1:
				my_dict["BeatDuration"] = float(items[1])
				inherited = my_dict["BeatDuration"]
			else:
				my_dict["BeatDuration"] = max(10.0, min(1000.0, -float(items[1]))) * inherited / 100
			my_dict["Base"] = inherited
			my_dict["Meter"] = int(items[2])
			my_dict["SampleSet"] = items[3]
			my_dict["SampleIndex"] = items[4]
			my_dict["Volume"] = float(items[5])
			# my_dict["Kiai"] = int(items[7])
			self.timing_point.append(my_dict)
		self.timing_point.append({"Offset": float('inf')})

	def istacked(self, curobj, prevobj, t_min, end=""):
		x1, y1 = curobj["x"], curobj["y"]
		x2, y2 = prevobj[end + "x"], prevobj[end + "y"]
		t1, t2 = curobj["time"], prevobj[end + "time"]
		return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < 3 and t1 - t2 < t_min

	def parse_hitobject(self):
		hitobject = self.info["HitObjects"]
		hitobject = hitobject.split("\n")
		cur_combo_number = 1
		cur_combo_color = 1

		index = 0

		cur_offset = 0

		for item in hitobject:
			if item == '':
				continue
			my_dict = {}
			osuobject = item.split(",")

			if self.hr:
				osuobject[1] = 384 - int(osuobject[1])

			my_dict["x"] = int(osuobject[0])
			my_dict["y"] = int(osuobject[1])
			my_dict["time"] = int(osuobject[2])
			my_dict["id"] = index

			# use next off_set or not
			while my_dict["time"] >= self.timing_point[cur_offset + 1]["Offset"]:
				cur_offset += 1
			my_dict["BeatDuration"] = self.timing_point[cur_offset]["BeatDuration"]
			bin_info = "{0:{fill}8b}".format(int(osuobject[3]), fill='0')  # convert int to binary, make it 8-bits
			bin_info = bin_info[::-1]  # reverse the binary
			object_type = []
			skip = 0

			my_dict["stacking"] = 0

			if int(bin_info[0]):
				object_type.append("circle")
				my_dict["end time"] = my_dict["time"]
				my_dict["end x"] = my_dict["x"]
				my_dict["end y"] = my_dict["y"]
				my_dict["hitSound"] = osuobject[4]
				if len(osuobject) > 5:
					my_dict["hitSample"] = osuobject[5]
				else:
					my_dict["hitSample"] = "0:0:0:0:"

			if int(bin_info[2]):
				object_type.append("new combo")
				if cur_combo_color not in self.max_combo or cur_combo_number > self.max_combo[cur_combo_color]:
					self.max_combo[cur_combo_color] = cur_combo_number
				cur_combo_number = 1
				skip = 1
				n_combo = bin_info[4:7]
				n_combo = int(n_combo[::-1], 2)
				skip += n_combo
				cur_combo_color += skip
				while cur_combo_color > self.ncombo:
					cur_combo_color = cur_combo_color - self.ncombo

			if int(bin_info[1]):
				object_type.append("slider")
				if cur_combo_number in self.slider_combo:
					self.slider_combo[cur_combo_number].add(cur_combo_color)
				else:
					self.slider_combo[cur_combo_number] = {cur_combo_color}

				my_dict["head not done"] = True  # for judgement

				ps = [[my_dict["x"], my_dict["y"]]]
				slider_path = osuobject[5]
				slider_path = slider_path.split("|")
				slider_type = slider_path[0]
				slider_path = slider_path[1:]
				for pos in slider_path:
					pos = pos.split(":")
					if self.hr:
						pos[1] = 384 - int(pos[1])
					ps.append([int(pos[0]), int(pos[1])])
				my_dict["ps"] = ps
				my_dict["slider type"] = slider_type
				my_dict["pixel length"] = float(osuobject[7])
				baiser = getclass(slider_type, ps, my_dict["pixel length"])
				my_dict["baiser"] = baiser

				my_dict["repeated"] = int(osuobject[6])
				my_dict["duration"] = my_dict["BeatDuration"] * my_dict["pixel length"] / (
						100 * self.diff["SliderMultiplier"])
				my_dict["end time"] = my_dict["duration"] * my_dict["repeated"] + my_dict["time"]

				end_goingforward = my_dict["repeated"] % 2 == 1
				endpos, _ = baiser.at(int(end_goingforward) * my_dict["pixel length"], None)
				my_dict["end x"] = int(endpos[0])
				my_dict["end y"] = int(endpos[1])

				my_dict["slider ticks"] = []
				my_dict["ticks pos"] = []
				my_dict["arrow pos"], _ = baiser.at(my_dict["pixel length"] * 0.98, None)
				speedmultiplier = self.timing_point[cur_offset]["Base"] / my_dict["BeatDuration"]
				scoring_distance = 100 * self.diff["SliderMultiplier"] * speedmultiplier
				mindist_fromend = scoring_distance / self.timing_point[cur_offset]["Base"] * 10
				tickdistance = min(my_dict["pixel length"], max(0, scoring_distance / self.diff["SliderTickRate"]))

				# source: https://github.com/ppy/osu/blob/73467410ab0917594eb9613df6e828e1a24c6be6/osu.Game/Rulesets/Objects/SliderEventGenerator.cs#L123
				my_dict["ticks dist"] = []
				d = tickdistance
				while d < my_dict["pixel length"] - mindist_fromend:
					pos, t = baiser.at(d, True)
					my_dict["slider ticks"].append(t)
					my_dict["ticks pos"].append(pos)
					my_dict["ticks dist"].append(d)
					d += tickdistance
				# print(len(my_dict["slider ticks"]))

				baiser.clear()

				my_dict["hitSound"] = osuobject[4]
				if len(osuobject) > 9:
					my_dict["edgeSounds"] = osuobject[8]
					my_dict["edgeSets"] = osuobject[9]
					if len(osuobject) > 10:
						my_dict["hitSample"] = osuobject[10]
					else:
						my_dict["hitSample"] = "0:0:0:0:"
				else:
					my_dict["edgeSounds"] = osuobject[4]
					my_dict["edgeSets"] = "0:0"
					for i in range(my_dict["repeated"]):
						my_dict["edgeSounds"] += "|{}".format(osuobject[4])
						my_dict["edgeSets"] += "|0:0"
					my_dict["hitSample"] = "0:0:0:0:"

			if int(bin_info[3]):
				object_type.append("spinner")
				endtime = osuobject[5].split(":")[0]
				my_dict["end time"] = int(endtime)
				my_dict["end x"] = -1
				my_dict["end y"] = -1
				if len(osuobject) > 6:
					my_dict["hitSample"] = osuobject[6]
				else:
					my_dict["hitSample"] = "0:0:0:0:"

			my_dict["combo_color"] = cur_combo_color
			my_dict["combo_number"] = cur_combo_number
			my_dict["type"] = object_type
			my_dict["skip"] = skip
			my_dict["sound"] = int(osuobject[4])

			#
			# if index != 0 and not int(bin_info[3]) and "spinner" not in self.hitobjects[-1]["type"]:
			# 	prevobj = self.hitobjects[-1]
			# 	if self.istacked(my_dict, prevobj, min_stacktime) and "slider" not in prevobj["type"] and not reverse:
			# 		if stacking:
			# 			self.to_stack[-1]["end"] = index
			# 		else:
			# 			self.to_stack.append({"start": index - 1, "end": index, "reverse": False})
			# 			stacking = True
			#
			# 	elif self.istacked(my_dict, prevobj, min_stacktime, "end ") and "slider" not in my_dict["type"]:
			# 		if stacking:
			# 			self.to_stack[-1]["end"] = index
			# 		else:
			# 			self.to_stack.append({"start": index, "end": index, "reverse": True})
			# 			stacking = True
			# 			reverse = True
			#
			# 	else:
			# 		stacking = False
			# 		reverse = False
			# else:
			# 	stacking = False
			# 	reverse = False

			self.hitobjects.append(my_dict)
			cur_combo_number += 1
			index += 1
		self.start_time = self.hitobjects[0]["time"]
		self.end_time = self.hitobjects[-1]["end time"]

	def enddistance(self, obj1, obj2):
		return math.sqrt((obj1["end x"] - obj2["x"]) ** 2 + (obj1["end y"] - obj2["y"]) ** 2)

	def distance(self, obj1, obj2):
		return math.sqrt((obj1["x"] - obj2["x"]) ** 2 + (obj1["y"] - obj2["y"]) ** 2)

	def stack_position(self):
		scale = (1.0 - 0.7 * (self.diff["CircleSize"] - 5) / 5) / 2
		stack_space = scale * 6.4
		# for info in self.to_stack:
		# 	for i in range(info["end"] - info["start"] + 1):
		# 		if info["reverse"]:
		# 			space = (i+1) * scale * 6.4
		# 		else:
		# 			space = (info["end"] - info["start"] - i) * scale * -6.4
		# 		index = info["start"] + i
		#
		# 		if "slider" in self.hitobjects[index]["type"]:
		# 			self.hitobjects[index]["stacking"] = space
		# 			self.hitobjects[index]["end x"] += space
		# 			self.hitobjects[index]["end y"] += space
		#
		# 		self.hitobjects[index]["x"] += space
		# 		self.hitobjects[index]["y"] += space

		ar = self.diff["ApproachRate"]  # for stacks
		if ar < 5:
			preempt = 1200 + 600 * (5 - ar) / 5
		elif ar == 5:
			preempt = 1200
		else:
			preempt = 1200 - 750 * (ar - 5) / 5

		cur_offset = 0
		stackThreshold = preempt * self.general["StackLeniency"]
		stack_distance = 3

		endIndex = len(self.hitobjects) - 1
		extendedEndIndex = endIndex

		startIndex = 0
		# Reverse pass for stack calculation.
		extendedStartIndex = startIndex

		for i in range(extendedEndIndex, startIndex, -1):

			n = i
			""" We should check every note which has not yet got a stack.
				* Consider the case we have two erwound stacks and this will make sense.
				*
				* o <-1      o <-2
				*  o <-3      o <-4
				*
				* We first process starting from 4 and handle 2,
				* then we come backwards on the i loop iteration until we reach 3 and handle 1.
				* 2 and 1 will be ignored in the i loop because they already have a stack value.
			"""

			objectI = self.hitobjects[i]
			if objectI["stacking"] != 0 or "spinner" in objectI["type"]:
				continue

			""" If this object is a hitcircle, then we enter this "special" case.
				* It either ends with a stack of hitcircles only, or a stack of hitcircles that are underneath a slider.
				* Any other case is handled by the "is Slider" code below this.
			"""
			if "circle" in objectI["type"]:
				n -= 1
				while n >= 0:
					objectN = self.hitobjects[n]
					if "spinner" in objectN:
						n -= 1
						continue

					if objectI["time"] - objectN["end time"] > stackThreshold:
						break

					endTime = objectN["end time"]

					if objectI["time"] - endTime > stackThreshold:
						# We are no longer within stacking range of the previous object.
						break

					# HitObjects before the specified update range haven't been reset yet
					if n < extendedStartIndex:
						objectN["stacking"] = 0
						extendedStartIndex = n

					""" This is a special case where hticircles are moved DOWN and RIGHT (negative stacking) if they are under the *last* slider in a stacked pattern.
						*    o==o <- slider is at original location
						*        o <- hitCircle has stack of -1
						*         o <- hitCircle has stack of -2
					"""
					if "slider" in objectN["type"] and self.enddistance(objectN, objectI) < stack_distance:
						offset = objectI["stacking"] - objectN["stacking"] + 1

						for j in range(n + 1, i + 1):

							# For each object which was declared under this slider, we will offset it to appear
							# *below* the slider end (rather than above).
							objectJ = self.hitobjects[j]
							if self.enddistance(objectN, objectJ) < stack_distance:
								objectJ["stacking"] -= offset

						# We have hit a slider.  We should restart calculation using this as the new base.
						# Breaking here will mean that the slider still has StackCount of 0, so will be handled in the i-outer-loop.
						break

					if self.distance(objectN, objectI) < stack_distance:
						# Keep processing as if there are no sliders.  If we come across a slider, this gets cancelled out.
						# NOTE: Sliders with start positions stacking are a special case that is also handled here.

						objectN["stacking"] = objectI["stacking"] + 1
						objectI = objectN

					n -= 1

			elif "slider" in objectI["type"]:
				""" We have hit the first slider in a possible stack.
						* From this po on, we ALWAYS stack positive regardless.
				"""
				n -= 1
				while n >= startIndex:
					objectN = self.hitobjects[n]
					if "spinner" in objectN["type"]:
						n -= 1
						continue

					if objectI["time"] - objectN["time"] > stackThreshold:
						# We are no longer within stacking range of the previous object.
						break

					if self.enddistance(objectN, objectI) < stack_distance:
						objectN["stacking"] = objectI["stacking"] + 1
						objectI = objectN

					n -= 1

		for osuobj in self.hitobjects:
			if "spinner" in osuobj["type"]:
				continue

			space = -stack_space * osuobj["stacking"]
			osuobj["x"] += space
			osuobj["y"] += space
			osuobj["end x"] += space
			osuobj["end y"] += space


def split(delimiters, string):
	lines = string.split("\n")
	curheader = "dummy"
	info = {curheader: ""}
	newheader = False
	for line in lines:
		line = line.strip()
		if line == "":
			continue

		for header in delimiters:
			if header == line:
				header = header[1:-1]
				info[header] = ""
				newheader = True
				curheader = header

		if not newheader:
			info[curheader] += line + "\n"
		newheader = False
	return info


def read_file(filename, scale, colors, hr):
	fiel = open(filename, "r", encoding="utf-8")
	content = fiel.read()
	delimiters = ["[General]", "[Editor]", "[Metadata]", "[Difficulty]", "[Events]", "[TimingPoints]", "[Colours]",
	              "[HitObjects]"]
	info = split(delimiters, content)
	fiel.close()
	bmap = Beatmap(info, scale, colors, hr)
	bmap.path = filename
	return bmap
