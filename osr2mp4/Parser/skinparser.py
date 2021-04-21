from configparser import ConfigParser
from collections import OrderedDict
from pathlib import Path
from osr2mp4 import logger


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



def raw(text: str):
	"""
	Returns a raw string representation of text
	

	^^ wdym bro
	"""
	res = ''
	for char in text:
		if char in escape_dict:
			res += escape_dict[char]
		else:
			res += char
			
	return res

class MultiOrderedDict(OrderedDict): # added back cuz the parser overwrite shit so yea
	def __setitem__(self, key, value):
		if isinstance(value, list) and key in self:
			return

		super().__setitem__(key, value)

class Skin:
	skin_path: Path = ''
	default_path: Path = ''
	# sections
	general: dict = {}
	colours: dict = {}
	fonts: dict = {}

	# internal, mostly for debugging
	# sections: dict = {} # no longer used
	# config: ConfigParser = None


	def __init__(self, skin_path: str, default_path: str, inipath: str = None): # i want to change the inipath to ini_path but considering 
		self.skin_path = Path(skin_path) / 'skin.ini'                     # that it might break something i dont
		self.default_path = Path(default_path) / 'skin.ini'

		if inipath:
			self.default_path = self.skin_path = Path(inipath)

		self.read()
		self.parse_general()
		self.parse_colours()
		self.parse_fonts()

	@staticmethod
	def filter(lines: str):
		""" Remove bullshit """
		while lines[0] != '[':
			lines = lines[1:]

		res = ''
		for line in lines.split('\n'):
			line = line.strip()

			# 1st line is basic checking
			# 2st checks for comments or some weird bullshit (from cpol skin mostly)
			# ok so i need to change the way it filters cuz in tests skin-3.ini is some weird shit and it fucks with the parser
			if not line or (':' not in line and '[' not in line)\
				or line[0] == '/' or line[0] == '#':
				line = ''

			res += line + '\n'

		return res.replace("//", " //").replace('\x00', '')

	@staticmethod
	def int(text: str):
		""" Convert string into integer but safe """
		res = ''
		for char in str(text):
			if char.isdigit() or char == '-':
				res += char
			else:
				break

		return int(res)


	def read(self):
		parser = ConfigParser(strict=False, comment_prefixes=["//", "\\"], inline_comment_prefixes="//", dict_type=MultiOrderedDict)
		parser.optionxform = str # need to do this else the keys will be in lowercase



		if self.skin_path.exists():
			lines = self.skin_path.read_text(encoding='utf-8', errors='ignore')
		elif self.default_path.exists():
			lines = self.default_path.read_text(encoding='utf-8', errors='ignore')
		else:
			raise Exception('Failed to get skin.ini files.')

		parser.read_string(self.filter(lines))

		for section in ['General', 'Colours', 'Fonts']:
			if parser.has_section(section):
				setattr(self, section.lower(), dict(parser[section])) # epic hax
			else:
				setattr(self, section.lower(), {}) # epic hax

		# self.config = lines


	def parse_general(self):
		general = self.general
		general['CursorRotate'] = self.int(general.get('CursorRotate', 0))
		general['CursorExpand'] = self.int(general.get('CursorExpand', 0))
		general['CursorCentre'] = self.int(general.get('CursorCentre', 0))
		general['HitCircleOverlayAboveNumber'] = self.int(general.get('HitCircleOverlayAboveNumber', 0))
		general['SliderStyle'] = self.int(general.get('SliderStyle', 0))
		general['AllowSliderBallTint'] = self.int(general.get('AllowSliderBallTint', 0))
		general['SliderBallFlip'] = self.int(general.get('SliderBallFlip', 0))
		general['AnimationFramerate'] = self.int(general.get('AnimationFramerate', 60))
		general['Version'] = general.get('Version', 1.0)

		if general['Version'] != 'latest':
			general['Version'] = self.int(general['Version'])



	def parse_colours(self):
		for key, val in self.colours.items():
			val = val.split(',')
			for n, c in enumerate(val):
				val[n] = int(c)

			self.colours[key] = val

		colours = self.colours

		cur_combo = 1
		while True:
			combo = f'Combo{cur_combo}'
			if combo in colours:
				cur_combo += 1
			else:
				break
		cur_combo -= 1


		if cur_combo == 0:
			# use the default value
			cur_combo = 4
			colours["Combo1"] = (255, 192, 0)
			colours["Combo2"] = (0, 202, 0)
			colours["Combo3"] = (18, 124, 255)
			colours["Combo4"] = (242, 24, 57)

		colours['InputOverlayText'] = colours.get('InputOverlayText', (0, 0, 0))
		colours["SliderBall"] = colours.get("SliderBall", (2, 170, 255))
		colours["SliderBorder"] = colours.get("SliderBorder", (255, 255, 255))
		colours["SliderTrackOverride"] = colours.get("SliderTrackOverride", (0, 0, 0))  # TODO: use current combo color
		colours["SpinnerBackground"] = colours.get("SpinnerBackground", (100, 100, 100))
		colours['ComboNumber'] = cur_combo

		

		

	def parse_fonts(self):
		fonts = self.fonts
		fonts['HitCircleOverlap'] = self.int(fonts.get('HitCircleOverlap', -2))
		fonts['ScoreOverlap'] = self.int(fonts.get('ScoreOverlap', -2))
		fonts['ComboOverlap'] = self.int(fonts.get('ScoreOverlap', -2))


		#### tbh idk what the raw is for but we'll see...
		fonts['ComboPrefix'] = fonts.get('ComboPrefix', 'score').strip()
		fonts['ComboPrefix'] = raw(fonts['ComboPrefix'])

		fonts['ScorePrefix'] = fonts.get('ScorePrefix', 'score').strip()
		fonts['ScorePrefix'] = raw(fonts['ScorePrefix'])

		fonts['HitCirclePrefix'] = fonts.get('HitCirclePrefix', 'default').strip()
		fonts['HitCirclePrefix'] = raw(fonts['HitCirclePrefix'])



if __name__ == "__main__":
	skin = Skin("../res/default/", "../res/default/")
	#skin = SkinParser("../../res/skin1/", "../res/default/")
