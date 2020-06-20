import math
import re
from ..ImageProcess.Curves.curves import getclass


class Beatmap:
	def __init__(self, info, scale, colors, hr):
		self.info = info
		self.general = {}
		self.diff = {}
		self.meta = {}
		self.bg = []
		self.breakperiods = []
		self.timing_point = []
		self.hitobjects = []
		self.sliderimg = {}
		self.max_combo = {}
		self.slider_combo = {}  # array of combo that are sliders. to prepare slider frames with those combo
		self.to_stack = []
		self.scale = scale

		self.ncombo = colors["ComboNumber"]
		self.hr = hr

		self.parse_general()
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
		general = self.info[1]
		general = general.split("\n")
		for item in general:
			if item != "":
				my_list = item.split(": ")
				self.general[my_list[0]] = float(my_list[1]) if my_list[1].replace('.', '', 1).isdigit() else my_list[1]

	def parse_meta(self):
		general = self.info[3]
		general = general.split("\n")
		for item in general:
			if item != "":
				my_list = item.split(":")
				self.meta[my_list[0]] = float(my_list[1]) if my_list[1].replace('.', '', 1).isdigit() else my_list[1]

	def parse_diff(self):
		general = self.info[4]
		general = general.split("\n")
		for item in general:
			if item != "":
				my_list = item.split(":")
				self.diff[my_list[0]] = float(my_list[1]) if my_list[1].replace('.', '', 1).isdigit() else my_list[1]
				self.diff["Base" + my_list[0]] = self.diff[my_list[0]]

	def parse_event(self):
		event = self.info[5].split("\n")

		for line in event:
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
			my_dict["Base"] = inherited
			my_dict["Meter"] = int(items[2])
			my_dict["SampleSet"] = items[3]
			my_dict["SampleIndex"] = items[4]
			my_dict["Volume"] = float(items[5])
			my_dict["Kiai"] = int(items[7])
			self.timing_point.append(my_dict)
		self.timing_point.append({"Offset": float('inf')})

	def istacked(self, curobj, prevobj, t_min, end=""):
		x1, y1 = curobj["x"], curobj["y"]
		x2, y2 = prevobj[end+"x"], prevobj[end+"y"]
		t1, t2 = curobj["time"], prevobj[end+"time"]
		return math.sqrt((x1 - x2)**2 + (y1 - y2)**2) < 3 and t1 - t2 < t_min

	def parse_hitobject(self):
		hitobject = self.info[-1]
		hitobject = hitobject.split("\n")
		cur_combo_number = 1
		cur_combo_color = 1

		index = 0
		stacking = False
		reverse = False

		ar = self.diff["ApproachRate"]  # for stacks
		if ar < 5:
			preempt = 1200 + 600 * (5 - ar) / 5
		elif ar == 5:
			preempt = 1200
		else:
			preempt = 1200 - 750 * (ar - 5) / 5

		cur_offset = 0
		min_stacktime = preempt * self.general["StackLeniency"]

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

				my_dict["stacking"] = 0

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
				speedmultiplier = self.timing_point[cur_offset]["Base"]/my_dict["BeatDuration"]
				scoring_distance = 100 * self.diff["SliderMultiplier"] * speedmultiplier
				mindist_fromend = scoring_distance/self.timing_point[cur_offset]["Base"] * 10
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


			if index != 0 and not int(bin_info[3]) and "spinner" not in self.hitobjects[-1]["type"]:
				prevobj = self.hitobjects[-1]
				if self.istacked(my_dict, prevobj, min_stacktime) and "slider" not in prevobj["type"] and not reverse:
					if stacking:
						self.to_stack[-1]["end"] = index
					else:
						self.to_stack.append({"start": index - 1, "end": index, "reverse": False})
						stacking = True

				elif self.istacked(my_dict, prevobj, min_stacktime, "end ") and "slider" not in my_dict["type"]:
					if stacking:
						self.to_stack[-1]["end"] = index
					else:
						self.to_stack.append({"start": index, "end": index, "reverse": True})
						stacking = True
						reverse = True

				else:
					stacking = False
					reverse = False
			else:
				stacking = False
				reverse = False

			self.hitobjects.append(my_dict)
			cur_combo_number += 1
			index += 1
		self.start_time = self.hitobjects[0]["time"]
		self.end_time = self.hitobjects[-1]["end time"]

	def stack_position(self):
		scale = (1.0 - 0.7 * (self.diff["CircleSize"] - 5) / 5) / 2
		for info in self.to_stack:
			for i in range(info["end"] - info["start"] + 1):
				if info["reverse"]:
					space = (i+1) * scale * 6.4
				else:
					space = (info["end"] - info["start"] - i) * scale * -6.4
				index = info["start"] + i

				if "slider" in self.hitobjects[index]["type"]:
					self.hitobjects[index]["stacking"] = space
					self.hitobjects[index]["end x"] += space
					self.hitobjects[index]["end y"] += space

				self.hitobjects[index]["x"] += space
				self.hitobjects[index]["y"] += space


def split(delimiters, string):
	regrex_pattern = "|".join(map(re.escape, delimiters))
	return re.split(regrex_pattern, string)


def read_file(filename, scale, colors, hr):
	fiel = open(filename, "r", encoding="utf-8")
	content = fiel.read()
	delimiters = ["[General]", "[Editor]", "[Metadata]", "[Difficulty]", "[Events]", "[TimingPoints]", "[Colours]", "[HitObjects]"]
	info = split(delimiters, content)
	fiel.close()
	return Beatmap(info, scale, colors, hr)
