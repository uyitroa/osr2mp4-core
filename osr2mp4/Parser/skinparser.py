# done by Kysan the gay pp farmer thanks


# return pos of the first char of the  comment or -1 if there is no comment
import logging
import os
from collections import OrderedDict
from configparser import ConfigParser


def detect_comments(line):
	ancient_char = ''
	for k in range(len(line)):
		if line[k] == '/' and ancient_char == '/':
			return k
		ancient_char = line[k]
	return -1


def del_comment(line):
	i = detect_comments(line)
	if i != -1:
		line = line[: i - 1]
	return line.strip()


escape_dict = {'\a': '/a',
			   '\b': '/b',
			   '\c': '/c',
			   '\f': '/f',
			   '\n': '/n',
			   '\r': '/r',
			   '\t': '/t',
			   '\v': '/v',
			   '\'': "/'",
			   '\"': '/"',
			   '\\': '/',
			   ' ': '',
			   '\ufeff': ''}


def raw(text):
	"""Returns a raw string representation of text"""
	new_string = ''
	for char in text:
		try:
			new_string += escape_dict[char]
		except KeyError:
			new_string += char
	return new_string


def iint(text):
	new_string = ''
	for char in str(text):
		if char.isdigit() or char == '-':
			new_string += char
		else:
			break
	return int(new_string)


def getsection(config: ConfigParser, section):
	if config.has_section(section):
		return dict(config[section])
	return {}


# settings = {}  # why not put all sections into it at the end ?


class MultiOrderedDict(OrderedDict):
	def __setitem__(self, key, value):
		if isinstance(value, list) and key in self:
			return

		super().__setitem__(key, value)


class Skin:
	def __init__(self, skin_path, default_path, inipath=None):
		# sections
		self.general = {}
		self.colours = {}
		self.fonts = {}
		self.catchTheBeat = {}
		self.mania = {}
		self.skin_path = os.path.join(skin_path, "skin.ini")
		self.default_path = os.path.join(default_path, "skin.ini")

		if inipath is not None:
			self.skin_path = self.default_path = inipath


		self.read()
		self.parse_general()
		self.parse_colors()
		self.parse_fonts()

		# print(self.general)
		# print(self.colours)
		# print(self.fonts)

	def filter(self, string):
		start = "["
		while string[0] != start:
			string = string[1:]

		newstring = ""
		for line in string.split("\n"):
			l = line.strip()
			if ":" not in line and "[" not in line:
				l = ""
			newstring += l + "\n"
		return newstring.replace('\x00', '')

	def read(self):
		config = ConfigParser(strict=False, comment_prefixes="//", inline_comment_prefixes="//", dict_type=MultiOrderedDict)
		config.optionxform = str

		try:
			with open(self.skin_path, encoding='utf-8', errors='ignore') as file:
				lines = file.read()
		except FileNotFoundError:
			with open(self.default_path, encoding='utf-8', errors='ignore') as file:
				lines = file.read()
		lines = self.filter(lines)
		config.read_string(lines)

		self.general = getsection(config, "General")
		self.colours = getsection(config, "Colours")
		self.fonts = getsection(config, "Fonts")

		logging.log(1, self.general)
		logging.log(1, self.colours)
		logging.log(1, self.fonts)

	def parse_general(self):
		self.general['CursorRotate'] = iint(self.general.get('CursorRotate', 0))
		self.general['CursorExpand'] = iint(self.general.get('CursorExpand', 0))
		self.general['CursorCentre'] = iint(self.general.get('CursorCentre', 0))
		self.general['HitCircleOverlayAboveNumer'] = iint(self.general.get('HitCircleOverlayAboveNumer', 0))
		self.general['SliderStyle'] = iint(self.general.get('SliderStyle', 0))
		self.general['AllowSliderBallTint'] = iint(self.general.get('AllowSliderBallTint', 0))
		self.general['SliderBallFlip'] = iint(self.general.get('SliderBallFlip', 1))
		self.general['AnimationFramerate'] = iint(self.general.get('AnimationFramerate', 60))
		self.general['Version'] = self.general.get('Version', 1.0)
		if self.general['Version'] != "latest":
			self.general['Version'] = iint(self.general['Version'])

	def parse_colors(self):
		for key, value in self.colours.items():
			value = value.split(",")
			for x in range(len(value)):
				value[x] = int(value[x])
			self.colours[key] = value

		cur_combo = 1
		while True:
			n = "Combo" + str(cur_combo)
			if n in self.colours:
				cur_combo += 1
			else:
				break
		cur_combo -= 1

		if cur_combo == 0:
			self.colours["Combo1"] = self.colours.get("Combo1", (255, 192, 0))
			self.colours["Combo2"] = self.colours.get("Combo2", (0, 202, 0))
			self.colours["Combo3"] = self.colours.get("Combo3", (18, 124, 255))
			self.colours["Combo4"] = self.colours.get("Combo4", (242, 24, 57))
			cur_combo = 4
		self.colours["InputOverlayText"] = self.colours.get("InputOverlayText", (0, 0, 0))
		self.colours["SliderBall"] = self.colours.get("SliderBall", (2, 170, 255))
		self.colours["SliderBorder"] = self.colours.get("SliderBorder", (255, 255, 255))
		self.colours["SliderTrackOverride"] = self.colours.get("SliderTrackOverride", (0, 0, 0))  # TODO: use current combo color
		self.colours["SpinnerBackground"] = self.colours.get("SpinnerBackground", (100, 100, 100))
		self.colours["ComboNumber"] = cur_combo

	def parse_fonts(self):
		self.fonts['HitCircleOverlap'] = iint(self.fonts.get('HitCircleOverlap', -2))
		self.fonts['ScoreOverlap'] = iint(self.fonts.get('ScoreOverlap', -2))
		self.fonts['ComboOverlap'] = iint(self.fonts.get('ScoreOverlap', -2))

		self.fonts['ComboPrefix'] = self.fonts.get('ComboPrefix', 'score')
		self.fonts['ComboPrefix'] = self.fonts['ComboPrefix'].replace(" ", "")
		self.fonts['ComboPrefix'] = raw(self.fonts['ComboPrefix'])

		self.fonts['ScorePrefix'] = self.fonts.get('ScorePrefix', 'score')
		self.fonts['ScorePrefix'] = self.fonts['ScorePrefix'].replace(" ", "")
		self.fonts['ScorePrefix'] = raw(self.fonts['ScorePrefix'])

		self.fonts['HitCirclePrefix'] = self.fonts.get('HitCirclePrefix', 'default')
		self.fonts['HitCirclePrefix'] = self.fonts['HitCirclePrefix'].replace(" ", "")
		self.fonts['HitCirclePrefix'] = raw(self.fonts['HitCirclePrefix'])


if __name__ == "__main__":
	skin = Skin("../../res/skin1/", "../../res/skin1/")
