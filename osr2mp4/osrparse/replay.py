import _lzma

from osr2mp4.Exceptions import NoDataReplay
from osr2mp4.osrparse.enums import GameMode, Mod
import lzma, struct, datetime


class ReplayEvent(object):
	def __init__(self, time_since_previous_action, x, y, keys_pressed):
		self.time_since_previous_action = time_since_previous_action
		self.x = x
		self.y = y
		self.keys_pressed = keys_pressed


class Replay(object):
	__BYTE = 1
	__SHORT = 2
	__INT = 4
	__LONG = 8

	#Order of field initilization matters.
	def __init__(self, replay_data: bytes = None):
		if replay_data is not None:
			self.offset = 0
			self.game_mode = None
			self.game_version = None
			self.beatmap_hash = None
			self.player_name = None
			self.replay_hash = None
			self.number_300s = None
			self.number_100s = None
			self.number_50s = None
			self.gekis = None
			self.katus = None
			self.misses = None
			self.score = None
			self.max_combo = None
			self.is_perfect_combo = None
			self.mod_combination = None
			self.life_bar_graph = None
			self.timestamp = None
			self.play_data = None
			#self.view = memoryview(replay_data) # FireRedz: stupid python cant pickle memoryview
			self.view = replay_data
			self.parse_replay_and_initialize_fields(replay_data)
		else:
			self.game_mode = 0
			self.game_version = ""
			self.beatmap_hash = ""
			self.player_name = "osu!"
			self.replay_hash = ""
			self.number_300s = 0
			self.number_100s = 0
			self.number_50s = 0
			self.gekis = 0
			self.katus = 0
			self.misses = 0
			self.score = float("inf")
			self.max_combo = 0
			self.is_perfect_combo = 1

			self.mod_combination = []

			self.life_bar_graph = ""
			self.timestamp = datetime.datetime.now()

	@classmethod
	def from_path(cls, path: str):
		with open(path, 'rb') as file:
			try:
				return cls(replay_data=file.read())
			except _lzma.LZMAError:
				raise NoDataReplay()
			except Exception as err:
				raise err


	def parse_replay_and_initialize_fields(self, replay_data: bytes):
		self.game_mode = self.read_byte()
		self.game_version = self.read_int()
		self.beatmap_hash = self.read_string()
		self.player_name = self.read_string()
		self.replay_hash = self.read_string()
		self.number_300s = self.read_short()
		self.number_100s = self.read_short()
		self.number_50s = self.read_short()
		self.gekis = self.read_short()
		self.katus = self.read_short()
		self.misses = self.read_short()
		self.score = self.read_int()
		self.max_combo = self.read_short()
		self.is_perfect_combo = self.read_byte()
		self.mods = self.read_int()
		self.parse_mod_combination()
		self.life_bar_graph = self.read_string()
		self.timestamp = datetime.datetime.min + datetime.timedelta(microseconds=self.read_long()/10)
		self.parse_play_data(replay_data)

	def parse_mod_combination(self):
		# Generator yielding value of each bit in an integer if it's set + value
		# of LSB no matter what .
		def bits(n):
			if n == 0:
				yield 0
			while n:
				b = n & (~n+1)
				yield b
				n ^= b

		bit_values_gen = bits(self.mod_combination)
		self.mod_combination = frozenset(Mod(mod_val) for mod_val in bit_values_gen)

	def parse_play_data(self, replay_data: bytes):
		frames = []
		lzma_len = self.read_int() # aka self.__replay_length
		lzma_raw = lzma.decompress(self.read_byte(lzma_len)).decode('ascii')[:-1]
		events = [event_raw.split('|') for event_raw in lzma_raw.split(',')]

		self.play_data = [
						ReplayEvent(
							int(event[0]),
							float(event[1]),
							float(event[2]),
							int(event[3])
							)
						for event in events
						]


	### NEW
	def read_byte(self, length: int = 1):
		val = self.view[:length]
		self.view = self.view[length:]
		return val

	def read_short(self):
		val = int.from_bytes(self.view[:2], 'little')
		self.view = self.view[2:]
		return val

	def read_int(self):
		val = int.from_bytes(self.view[:4], 'little')
		self.view = self.view[4:]
		return val

	def read_float(self):
		return self.read_int()

	def read_long(self):
		val = int.from_bytes(self.view[:8], 'little')
		self.view = self.view[8:]
		return val

	def read_double(self):
		return self.read_long()

	def read_uleb128(self):
		val = shift = 0

		while True:
			b = int.from_bytes(self.read_byte(), 'little')


			val |= ((b & 0b01111111) << shift)
			if (b & 0b10000000) == 0x00:
				break

			shift += 7

		return val

	def read_string(self):
		if self.read_byte() == 0x00:
			return ''

		raw = self.read_uleb128()
		return self.read_byte(raw).decode()




	def get(self):
		d = self.__dict__
		self_dict = {k: d[k] for k in d if k != 'play_data'}
		return self_dict

	def set(self, state: dict):
		self.__dict__ = state




def parse_replay_file(replay_path):
	return Replay.from_path(replay_path)

parse_replay = parse_replay_file