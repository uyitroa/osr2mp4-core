import unittest, datetime
from osrparse.replay import parse_replay, parse_replay_file, ReplayEvent
from osrparse.enums import GameMode, Mod


class TestStandardReplay(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('tests/resources/replay.osr', 'rb') as f:
            data = f.read()
        cls._replays = [parse_replay(data), parse_replay_file('tests/resources/replay.osr')]
        cls._combination_replay = parse_replay_file('tests/resources/replay2.osr')

    def test_replay_mode(self):
        for replay in self._replays:
            self.assertEqual(replay.game_mode, GameMode.Standard, "Game mode is incorrect")

    def test_game_version(self):
        for replay in self._replays:
            self.assertEqual(replay.game_version, 20140226, "Game version is incorrect")

    def test_beatmap_hash(self):
        for replay in self._replays:
            self.assertEqual(replay.beatmap_hash, "da8aae79c8f3306b5d65ec951874a7fb", "Beatmap hash is incorrect")

    def test_player_name(self):
        for replay in self._replays:
            self.assertEqual(replay.player_name, "Cookiezi", "Player name is incorrect")

    def test_number_hits(self):
        for replay in self._replays:
            self.assertEqual(replay.number_300s, 1982, "Number of 300s is wrong")
            self.assertEqual(replay.number_100s, 1, "Number of 100s is wrong")
            self.assertEqual(replay.number_50s, 0, "Number of 50s is wrong")
            self.assertEqual(replay.gekis, 250, "Number of gekis is wrong")
            self.assertEqual(replay.katus, 1, "Number of katus is wrong")
            self.assertEqual(replay.misses, 0, "Number of misses is wrong")

    def test_max_combo(self):
        for replay in self._replays:
            self.assertEqual(replay.max_combo, 2385, "Max combo is wrong")

    def test_is_perfect_combo(self):
        for replay in self._replays:
            self.assertEqual(replay.is_perfect_combo, True, "is_perfect_combo is wrong")

    def test_nomod(self):
        for replay in self._replays:
            self.assertEqual(replay.mod_combination, frozenset([Mod.NoMod]), "Mod combination is wrong")

    def test_mod_combination(self):
        self.assertEqual(self._combination_replay.mod_combination, frozenset([Mod.Hidden, Mod.HardRock]), "Mod combination is wrong")

    def test_timestamp(self):
        for replay in self._replays:
            self.assertEqual(replay.timestamp, datetime.datetime(2013, 2, 1, 16, 31, 34), "Timestamp is wrong")

    def test_play_data(self):
        for replay in self._replays:
            self.assertIsInstance(replay.play_data[0], ReplayEvent, "Replay data is wrong")
            self.assertEqual(len(replay.play_data), 17500, "Replay data is wrong")
