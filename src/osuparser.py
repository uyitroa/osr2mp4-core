import re


class Beatmap:
	def __init__(self, info):
		self.info = info
		self.general = {}
		self.diff = {}
		self.bg = []
		self.breakperiods = []
		self.timing_point = []
		self.hitobjects = []
		self.max_combo = 0
		self.to_stack = []

		self.parse_general()
		self.parse_diff()
		self.parse_event()
		self.parse_timingpoints()
		self.parse_hitobject()
		self.stack_position()
	# print("General:", self.general)
	# print("\n\nDiff:", self.diff)
	# print("\n\nBreak Periods:", self.breakperiods)
	# print("\n\nTiming points:", self.timing_point)
	# print("\n\nHitObjects:", self.hitobjects)

	def parse_general(self):
		general = self.info[1]
		general = general.split("\n")
		for item in general:
			if item != "":
				my_list = item.split(": ")
				self.general[my_list[0]] = float(my_list[1]) if my_list[1].replace('.', '', 1).isdigit() else my_list[1]

	def parse_diff(self):
		general = self.info[4]
		general = general.split("\n")
		for item in general:
			if item != "":
				my_list = item.split(":")
				self.diff[my_list[0]] = float(my_list[1]) if my_list[1].replace('.', '', 1).isdigit() else my_list[1]

	def parse_event(self):
		event = self.info[5]
		event = event.split("//")
		self.bg = event[1].split("\n")[1].split(",")

		breakperiods = event[2].split("\n")[1:-1]
		for period in breakperiods:
			my_dict = {}
			items = period.split(",")
			my_dict["Start"] = int(items[1])
			my_dict["End"] = int(items[2])
			self.breakperiods.append(my_dict)

	def parse_timingpoints(self):
		timing = self.info[6]
		timing = timing.split("\n")
		inherited = 0
		for line in timing:
			if line == '':
				continue
			my_dict = {}
			items = line.split(",")
			my_dict["Offset"] = float(items[0])
			if int(items[6]) == 1:
				my_dict["BeatDuration"] = float(items[1])
				inherited = my_dict["BeatDuration"]
			else:
				my_dict["BeatDuration"] = - float(items[1]) * inherited / 100
			my_dict["Meter"] = int(items[2])
			my_dict["SampleSet"] = int(items[3])
			my_dict["SampleIndex"] = int(items[4])
			my_dict["Volume"] = float(items[5])
			my_dict["Kiai"] = int(items[7])
			self.timing_point.append(my_dict)

	def parse_hitobject(self):
		hitobject = self.info[-1]
		hitobject = hitobject.split("\n")
		cur_combo_number = 1

		index = 0
		stacking = False

		ar = self.diff["ApproachRate"]
		if ar < 5:
			preempt = 1200 + 600 * (5 - ar) / 5
		elif ar == 5:
			preempt = 1200
		else:
			preempt = 1200 - 750 * (ar - 5) / 5

		for item in hitobject:
			if item == '':
				continue
			my_dict = {}
			osuobject = item.split(",")
			my_dict["x"] = int(osuobject[0])
			my_dict["y"] = int(osuobject[1])
			my_dict["time"] = int(osuobject[2])

			if index != 0:
				if my_dict["x"] == self.hitobjects[-1]["x"] and my_dict["y"] == self.hitobjects[-1]["y"] and \
						my_dict["time"] - self.hitobjects[-1]["time"] <= preempt * self.general["StackLeniency"]:
					if stacking:
						self.to_stack[-1]["end"] = index
					else:
						self.to_stack.append({"start": index - 1, "end": index})
						stacking = True
				else:
					stacking = False

			bin_info = "{0:{fill}8b}".format(int(osuobject[3]), fill='0')
			bin_info = bin_info[::-1]
			object_type = []
			skip = 0

			if int(bin_info[0]):
				object_type.append("circle")

			if int(bin_info[1]):
				object_type.append("slider")
				my_dict["slider_path"] = osuobject[5]
				my_dict["repeat"] = int(osuobject[6])
				my_dict["pixelLength"] = float(osuobject[7])
				if len(osuobject) > 9:
					my_dict["edgeHitsound"] = osuobject[8]
					my_dict["edgeAdditions"] = osuobject[9]

			if int(bin_info[2]):
				object_type.append("new combo")
				cur_combo_number = 1
				skip = 1
				n_combo = bin_info[4:7]
				n_combo = int(n_combo[::-1], 2)
				skip += n_combo

			if int(bin_info[3]):
				object_type.append("spinner")

			my_dict["combo_number"] = cur_combo_number
			my_dict["type"] = object_type
			my_dict["skip"] = skip
			my_dict["sound"] = int(osuobject[4])
			self.hitobjects.append(my_dict)
			cur_combo_number += 1
			if cur_combo_number > self.max_combo:
				self.max_combo = cur_combo_number
			index += 1

	def stack_position(self):
		for info in self.to_stack:
			space = -0.4 * self.diff["CircleSize"] + 4.9 # lol my own formula
			for i in range(info["start"] + 1, info["end"] + 1):
				self.hitobjects[i]["x"] += space
				self.hitobjects[i]["y"] += space
				space *= 2


def split(delimiters, string):
	regrex_pattern = "|".join(map(re.escape, delimiters))
	return re.split(regrex_pattern, string)


def read_file(filename):
	content = open(filename, "r").read()
	delimiters = ["[General]", "[Editor]", "[Metadata]", "[Difficulty]", "[Events]", "[TimingPoints]", "[Colours]",
	              "[HitObjects]"]
	info = split(delimiters, content)
	return Beatmap(info)


if __name__ == "__main__":
	read_file("../res/katayoku.osu")
