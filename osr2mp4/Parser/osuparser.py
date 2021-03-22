import math, os

from osr2mp4 import logger
from osr2mp4.Utils.maphash import osuhash
from osr2mp4.Exceptions import GameModeNotSupported, NotAnBeatmap


class Beatmap:
	def __init__(self, info: dict, scale: float = 1, colors: dict = None, mods: 'mods' = None, lazy: bool = True):
		self.info = info
		self.general = {"StackLeniency": 0.7, "Mode": 0}
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
		self.hash = None
		self.is2b = False
		self.start_time = 0
		self.end_time = 0

		if colors is None:
			colors = {"ComboNumber": 1}
		self.ncombo = colors["ComboNumber"]

		if mods is None:
			mods = []

		self.mods = mods

		self.parse_general()

		if self.general["Mode"] != 0:
			raise GameModeNotSupported()

		self.parse_meta()
		self.parse_diff()

		self.parse_event()
		self.parse_timingpoints()

		if not lazy:
			self.parse_hitobject()
			self.stack_position()

			endtime_fp = self.hitobjects[-1]["time"] + 800
			# diffcalculator = DiffCalculator(self.diff)
			# timepreempt = int(diffcalculator.ar() + 500)
			# self.breakperiods.append({"Start": -500, "End": self.start_time-timepreempt, "Arrow": True})
			self.hitobjects.append({"x": 0, "y": 0, "time": endtime_fp, "end time": endtime_fp, "combo_number": 0,
			                        "type": ["end"], "id": -1})  # to avoid index out of range

		else:
			self.parse_hitobjecttime()

		self.health_processor = None

	def parse_general(self):
		general = self.info["General"].split("\n")
		for item in general:
			item = item.strip()
			if item != "":
				name, value = item.split(":")
				value = value.strip()
				self.general[name] = float(value) if (value.replace('.', '', 1)).isdigit() else value

	def parse_meta(self):
		meta = self.info["Metadata"].split("\n")
		for item in meta:
			item = item.strip()
			if item != "":
				name, value = item.split(":")
				value = value.strip()
				self.meta[name] = float(value) if (value.replace('.', '', 1)).isdigit() else value

	def parse_diff(self):
		diff = self.info["Difficulty"].split("\n")
		for item in diff:
			item = item.strip()
			if item != "":
				name, value = item.split(":")
				value = value.strip()
				self.diff[name] = float(value) if value.replace('.', '', 1).isdigit() else value
				self.diff["Base" + name] = self.diff[name]

		self.diff["ApproachRate"] = self.diff.get("ApproachRate", self.diff["OverallDifficulty"])
		self.diff["BaseApproachRate"] = self.diff["ApproachRate"]

	def parse_event(self):
		events = self.info["Events"].split("\n")

		for line in events:
			line = line.strip()
			if line.startswith("0"):
				self.bg = line.split(",")
				self.bg[2] = self.bg[2].replace('"', '')
			if line.startswith("2"):
				event = {}
				items = line.split(",")
				event["Start"] = int(items[1])
				event["End"] = int(items[2])
				event["Arrow"] = True
				self.breakperiods.append(event)

	def parse_timingpoints(self):
		timings = self.info["TimingPoints"].split("\n")
		inherited = 0
		for line in timings:
			timing = {}
			try:
				line = line.strip()
				if not line:
					continue

				items = line.split(",")
				timing["Offset"] = float(items[0])

				if len(items) < 7 or int(items[6]) == 1:
					timing["BeatDuration"] = float(items[1])
					inherited = timing["BeatDuration"]
				else:
					timing["BeatDuration"] = max(10.0, min(1000.0, -float(items[1]))) * inherited / 100

				timing["Base"] = inherited
				timing["Meter"] = int(items[2])
				timing["SampleSet"] = items[3]
				timing["SampleIndex"] = items[4]
				timing["Volume"] = float(items[5])

			except Exception as e:
				timing["Meter"] = timing.get("Meter", 0)
				timing["SampleSet"] = timing.get("SampleSet", "0")
				timing["SampleIndex"] = timing.get("SampleIndex", "0")
				timing["Volume"] = timing.get("Volume", 100)
				self.timing_point.append(timing)
				logger.error(repr(e))
				continue

			# my_dict["Kiai"] = int(items[7])
			self.timing_point.append(timing)

		self.timing_point.append({"Offset": float('inf')})
		self.timing_point.append({"Offset": float('inf')}) # FireRedz: mega sus

	def istacked(self, curobj: dict, prevobj: dict, t_min: float, end: str = ""):
		x1, y1 = curobj["x"], curobj["y"]
		x2, y2 = prevobj[end + "x"], prevobj[end + "y"]
		t1, t2 = curobj["time"], prevobj[end + "time"]
		return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < 3 and t1 - t2 < t_min

	def parse_hitobjecttime(self):
		hitobjects = self.info["HitObjects"].split("\n")
		for item in hitobjects:
			if not item:
				continue

			osuobject = item.split(",")
			self.start_time = int(osuobject[2]) # FireRedz: wtf is this on reverse or something
			break
		for item in hitobject[::-1]:
			if not item:
				continue

			osuobject = item.split(",")
			bin_info = "{0:{fill}8b}".format(int(osuobject[3]), fill='0')  # convert int to binary, make it 8-bits
			bin_info = bin_info[::-1]  # reverse the binary
			osutime = int(osuobject[2])
			if int(bin_info[0]):
				self.end_time = osutime

			if int(bin_info[1]):
				cur_offset = 0
				while osutime >= self.timing_point[cur_offset + 1]["Offset"]:
					cur_offset += 1
				beatduration = self.timing_point[cur_offset]["BeatDuration"]
				length = float(osuobject[7])
				duration = beatduration * length / (100 * self.diff["SliderMultiplier"]) * int(osuobject[6])
				self.end_time = osutime + duration

			if int(bin_info[3]):
				endtime = osuobject[5].split(":")[0]
				self.end_time = int(endtime)
			break

	def parse_hitobject(self):
		from osr2mp4.osrparse.enums import Mod
		from osr2mp4.ImageProcess.Curves.curves import getclass

		hr = Mod.HardRock in self.mods

		hitobjects = self.info["HitObjects"].split("\n")
		cur_combo_number = 1
		cur_combo_color = 1

		index = 0

		cur_offset = 0

		for item in hitobjects:
			if not item:
				continue

			hitobject = {}
			osuobject = item.split(",")

			if hr:
				osuobject[1] = 384 - int(osuobject[1])

			hitobject["x"] = int(osuobject[0])
			hitobject["y"] = int(osuobject[1])
			hitobject["time"] = int(osuobject[2])
			hitobject["id"] = index

			while hitobject["time"] >= self.timing_point[cur_offset + 1]["Offset"]:
				cur_offset += 1
			hitobject["BeatDuration"] = self.timing_point[cur_offset]["BeatDuration"]
			bin_info = "{0:{fill}8b}".format(int(osuobject[3]), fill='0')  # convert int to binary, make it 8-bits # FireRedz: why
			bin_info = bin_info[::-1]  # reverse the binary
			object_type = []
			skip = 0

			hitobject["stacking"] = 0

			if int(bin_info[0]):
				object_type.append("circle")
				hitobject["end time"] = hitobject["time"]
				hitobject["end x"] = hitobject["x"]
				hitobject["end y"] = hitobject["y"]
				hitobject["hitSound"] = osuobject[4]
				if len(osuobject) > 5:
					hitobject["hitSample"] = osuobject[5]
				else:
					hitobject["hitSample"] = "0:0:0:0:"

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

				hitobject["head not done"] = True  # for judgement

				ps = [[hitobject["x"], hitobject["y"]]]
				slider_path = osuobject[5]
				slider_path = slider_path.split("|")
				slider_type = slider_path[0]
				slider_path = slider_path[1:]
				for pos in slider_path:
					pos = pos.split(":")
					if hr:
						pos[1] = 384 - int(pos[1])
					ps.append([int(pos[0]), int(pos[1])])
				hitobject["ps"] = ps
				hitobject["slider type"] = slider_type
				hitobject["pixel length"] = float(osuobject[7])
				slider_c = getclass(slider_type, ps, hitobject["pixel length"])
				hitobject["slider_c"] = slider_c

				hitobject["repeated"] = int(osuobject[6])
				hitobject["duration"] = hitobject["BeatDuration"] * hitobject["pixel length"] / (
						100 * self.diff["SliderMultiplier"])
				hitobject["end time"] = hitobject["duration"] * hitobject["repeated"] + hitobject["time"]
				hitobject["pixel length"] = slider_c.cum_length[-1]

				end_goingforward = hitobject["repeated"] % 2 == 1
				endpos = slider_c.at(int(end_goingforward) * hitobject["pixel length"])
				hitobject["end x"] = int(endpos[0])
				hitobject["end y"] = int(endpos[1])

				hitobject["slider ticks"] = []
				hitobject["ticks pos"] = []
				hitobject["arrow pos"] = slider_c.at(hitobject["pixel length"])
				speedmultiplier = self.timing_point[cur_offset]["Base"] / hitobject["BeatDuration"]
				scoring_distance = 100 * self.diff["SliderMultiplier"] * speedmultiplier
				mindist_fromend = scoring_distance / self.timing_point[cur_offset]["Base"] * 10
				tickdistance = min(hitobject["pixel length"], max(0, scoring_distance / self.diff["SliderTickRate"]))
				hitobject["tickdistance"] = tickdistance

				# source: https://github.com/ppy/osu/blob/73467410ab0917594eb9613df6e828e1a24c6be6/osu.Game/Rulesets/Objects/SliderEventGenerator.cs#L123
				hitobject["ticks dist"] = []
				d = tickdistance
				while d < hitobject["pixel length"] - mindist_fromend:
					pos = slider_c.at(d)
					hitobject["slider ticks"].append(d/hitobject["pixel length"])
					hitobject["ticks pos"].append(pos)
					hitobject["ticks dist"].append(d)
					d += tickdistance

				sliderscoringdistance = (100 * self.diff["SliderMultiplier"])/self.diff["SliderTickRate"]
				if hitobject["BeatDuration"] > 0:
					hitobject["velocity"] = sliderscoringdistance * self.diff["SliderTickRate"] * (1000/hitobject["BeatDuration"])
				else:
					hitobject["velocity"] = sliderscoringdistance * self.diff["SliderTickRate"]

				# logger.debug("%s %s", my_dict["velocity"], my_dict["pixel length"] / (my_dict["end time"] - my_dict["time"]) * 1000)

				hitobject["hitSound"] = osuobject[4]
				if len(osuobject) > 9:
					hitobject["edgeSounds"] = osuobject[8]
					hitobject["edgeSets"] = osuobject[9]
					if len(osuobject) > 10:
						hitobject["hitSample"] = osuobject[10]
					else:
						hitobject["hitSample"] = "0:0:0:0:"
				else:
					hitobject["edgeSounds"] = osuobject[4]
					hitobject["edgeSets"] = "0:0"
					for i in range(hitobject["repeated"]):
						hitobject["edgeSounds"] += "|{}".format(osuobject[4])
						hitobject["edgeSets"] += "|0:0"
					hitobject["hitSample"] = "0:0:0:0:"

			if int(bin_info[3]):
				object_type.append("spinner")
				endtime = osuobject[5].split(":")[0]
				hitobject["end time"] = int(endtime)
				hitobject["end x"] = -1
				hitobject["end y"] = -1
				if len(osuobject) > 6:
					hitobject["hitSample"] = osuobject[6]
				else:
					hitobject["hitSample"] = "0:0:0:0:"

			hitobject["combo_color"] = cur_combo_color
			hitobject["combo_number"] = cur_combo_number
			hitobject["type"] = object_type
			hitobject["skip"] = skip
			hitobject["sound"] = int(osuobject[4])

			if len(self.hitobjects) > 0 and self.hitobjects[-1]["end time"] >= hitobject["time"]:
				self.is2b = True
			self.hitobjects.append(hitobject)
			cur_combo_number += 1
			index += 1

		self.start_time = self.hitobjects[0]["time"]
		self.end_time = self.hitobjects[-1]["end time"]

	def enddistance(self, obj1, obj2):
		return math.sqrt((obj1["end x"] - obj2["x"]) ** 2 + (obj1["end y"] - obj2["y"]) ** 2)

	def distance(self, obj1, obj2):
		return math.sqrt((obj1["x"] - obj2["x"]) ** 2 + (obj1["y"] - obj2["y"]) ** 2)

	def stack_position(self):
		from osr2mp4.CheckSystem.mathhelper import getar, getcs

		cs = getcs(self.mods, self.diff["CircleSize"])
		scale = (1.0 - 0.7 * (cs - 5) / 5) / 2
		stack_space = scale * 6.4

		ar = getar(self.mods, self.diff["ApproachRate"], forstack=True)  # for stacks

		if ar < 5:
			preempt = 1200 + 600 * (5 - ar) / 5
		elif ar == 5:
			preempt = 1200
		else:
			preempt = 1200 - 750 * (ar - 5) / 5
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
						if objectN["time"] == 35878:
							print(objectN, objectI, stackThreshold)
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



def split(delimiters: list, string: str):
	lines = string.split('\n')
	info = {'dummy': ''}
	
	for line in lines:
		newheader = False
		curheader = 'dummy'
		line = line.strip()

		if not line:
			continue

		for header in delimiters:
			if header == line:
				header = header[1: -1]
				info[header] = ""
				newheader = True
				curheader = header

		if not newheader:
			info[curheader] += line + '\n'

	

	return info




def read_file(filename: str, scale: float = 1, colors: dict = None, mods=None, lazy=True, **kwargs: dict)
	if 'hr' in kwargs or 'dt' in kwargs:
		logger.warning("HR/DT args is deprecated.")

	# checks if filename is a path
	if os.path.isdir(filename):
		raise NotAnBeatmap()


	delimiters = ["[General]", "[Editor]", "[Metadata]", "[Difficulty]", 
				  "[Events]", "[TimingPoints]", "[Colours]", "[HitObjects]"]

	with open(filename , 'r', encoding='utf-8') as file:
		info = split(delimiters, file.read())


	bmap = Beatmap(info, scale, colors, mods=mods, lazy=lazy)
	bmap.path = filename
	bmap.hash = osuhash(filename)
	return bmap
