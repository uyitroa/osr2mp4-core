import math

from osr2mp4.CheckSystem.HitObjects.HitObject import HitObject
from osr2mp4.osrparse.enums import Mod
from osr2mp4.EEnum.EReplay import Replays


class Spinner(HitObject):
	WIDTH = 512
	HEIGHT = 384
	SIXTY_FRAME_TIME = 1000 / 60

	def __init__(self, hitobject):
		self.osu_d = hitobject
		self.rpm = 0
		self.cur_speed = 0
		self.theoretical_speed = 0
		self.prev_angle = 0
		self.frame_variance = 0
		self.rot_count = 0
		self.first = True
	
	def check(self, replay, osrindex):
		osr = replay[osrindex]

		if osr[Replays.TIMES] < self.osu_d["time"]:
			return False, None, None, None, 0, 0, 0

		if self.first:
			self.first = False
			timediff = self.SIXTY_FRAME_TIME
		else:
			timediff = osr[Replays.TIMES] - replay[max(0, osrindex-1)][Replays.TIMES]

		if osr[Replays.TIMES] >= self.osu_d["end time"]:
			rotation = (self.rot_count % 1) * 360
			spinrequired = self.diff.spinrequired(self.osu_d["end time"] - self.osu_d["time"])
			progress = self.rot_count / max(1, spinrequired)  # avoid divsion by 0 using max(1, spinrequired)

			if self.rot_count > spinrequired + 1 or Mod.SpunOut in self.mods:
				hitresult = 300
			elif self.rot_count > spinrequired:
				hitresult = 100
			elif self.rot_count >= 0.1 * spinrequired:
				hitresult = 50
			else:
				hitresult = 0

			return True, rotation, progress, hitresult, 0, 0, self.rpm

		duration = self.osu_d["end time"] - self.osu_d["time"]
		max_accel = 0.00008 + max(0, (5000 - duration) / 1000 / 2000)

		elapsedtime = timediff  # osr[Replays.TIMES] - replay[max(0, osrindex-1)][Replays.TIMES]

		cursor_vector_x = osr[Replays.CURSOR_X] - self.WIDTH/2
		cursor_vector_y = osr[Replays.CURSOR_Y] - self.HEIGHT/2
		cursor_angle = math.atan2(cursor_vector_y, cursor_vector_x)
		anglediff = cursor_angle - self.prev_angle

		if cursor_angle - self.prev_angle < -math.pi:
			anglediff = (2 * math.pi) + cursor_angle - self.prev_angle
		elif self.prev_angle - cursor_angle < -math.pi:
			anglediff = (-2 * math.pi) - self.prev_angle + cursor_angle

		decay = math.pow(0.999, timediff)
		self.frame_variance = decay * self.frame_variance + (1 - decay) * timediff

		if anglediff == 0:
			self.theoretical_speed /= 3
		else:
			if Mod.Relax not in self.mods and osr[Replays.KEYS_PRESSED] == 0:
				# print(osr[Replays.TIMES])
				anglediff = 0

			if abs(anglediff) < math.pi:
				# commented this block because it breaks spunout and auto mods
				# if self.diff.apply_mods_to_time(timediff, self.mods) > self.SIXTY_FRAME_TIME * 1.04:
				# 	self.theoretical_speed = anglediff / self.diff.apply_mods_to_time(timediff, self.mods)
				# else:
				self.theoretical_speed = anglediff / self.SIXTY_FRAME_TIME
			else:
				self.theoretical_speed = 0

		self.prev_angle = cursor_angle

		max_accel_this_frame = self.diff.apply_mods_to_time(max_accel * elapsedtime, self.mods)

		if Mod.SpunOut in self.mods:
			self.cur_speed = 0.03
		elif self.theoretical_speed > self.cur_speed:
			if self.cur_speed < 0 and Mod.Relax in self.mods:
				max_accel_this_frame /= self.diff.RELAX_BONUS_ACCEL

			self.cur_speed += min(self.theoretical_speed - self.cur_speed, max_accel_this_frame)
		else:
			if self.cur_speed > 0 and Mod.Relax in self.mods:
				max_accel_this_frame /= self.diff.RELAX_BONUS_ACCEL

			self.cur_speed += max(self.theoretical_speed - self.cur_speed, -max_accel_this_frame)

		self.cur_speed = max(-0.05, min(self.cur_speed, 0.05))

		decay = math.pow(0.9, elapsedtime / self.SIXTY_FRAME_TIME)
		rpm = self.rpm * decay + (1.0 - decay) * (abs(self.cur_speed) * 1000) / (math.pi * 2) * 60
		self.rpm = rpm

		prevcount = self.rot_count
		self.rot_count += rpm * timediff / 60000

		direction = -1 if self.cur_speed >= 0 else 1
		rotation = (self.rot_count * 360) % 360 * direction
		spinrequired = self.diff.spinrequired(duration)
		progress = self.rot_count / max(1, spinrequired)  # avoid divsion by 0 using max(1, spinrequired)
		bonus = max(0, int(self.rot_count - spinrequired - 3))

		rot_increased = int(self.rot_count) > int(prevcount)
		hitvalue = (self.rot_count > 1 and rot_increased and int(self.rot_count) % 2 == 0) * 100

		return True, rotation, progress, None, bonus, hitvalue, rpm
