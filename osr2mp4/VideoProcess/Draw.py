import PIL
import logging
import time

import cv2
from PIL import Image
from autologging import traced, logged, TRACE

from ..Utils.skip import skip
from ..InfoProcessor import Updater
from .AFrames import FrameObjects
from ..CheckSystem.Judgement import DiffCalculator
from ..EEnum.EReplay import Replays
from .smoothing import smoothcursor
from .Setup import FrameInfo, CursorEvent, get_buffer
from .calc import check_break, check_key, add_followpoints, add_hitobjects, nearer


class Drawer:
	def __init__(self, shared, beatmap, frames, replay_info, resultinfo, videotime, settings):
		self.shared = shared
		self.beatmap = beatmap
		self.frames = frames
		self.replay_info = replay_info
		self.replay_event = replay_info.play_data
		self.resultinfo = resultinfo
		self.start_index = videotime[0]
		self.end_index = videotime[1]
		self.settings = settings

		self.updater = None
		self.frame_info = None
		self.component = None
		self.preempt_followpoint = None
		self.cursor_event = None
		self.img = None
		self.time_preempt = None
		self.np_img, self.pbuffer = None, None
		self.initialised_ranking = False

		self.setup_draw()

	def setup_draw(self):
		replay_event = self.replay_info.play_data
		old_cursor_x = int(replay_event[0][Replays.CURSOR_X] * self.settings.playfieldscale) + self.settings.moveright
		old_cursor_y = int(replay_event[0][Replays.CURSOR_Y] * self.settings.playfieldscale) + self.settings.moveright

		diffcalculator = DiffCalculator(self.beatmap.diff)
		self.time_preempt = diffcalculator.ar()

		self.component = FrameObjects(self.frames, self.settings, self.beatmap, self.replay_info)

		self.component.cursor_trail.set_cursor(old_cursor_x, old_cursor_y, replay_event[0][Replays.TIMES])

		self.preempt_followpoint = 800

		self.updater = Updater(self.resultinfo, self.component)

		to_time = replay_event[self.start_index][Replays.TIMES]
		self.frame_info = FrameInfo(*skip(to_time, self.resultinfo, replay_event, self.beatmap, self.time_preempt, self.component))

		self.component.background.startbreak(self.beatmap.breakperiods[self.frame_info.break_index], self.frame_info.cur_time)

		self.cursor_event = CursorEvent(replay_event[self.frame_info.osr_index], old_cursor_x, old_cursor_y)

		self.updater.info_index = self.frame_info.info_index

		self.img = Image.new("RGB", (1, 1))
		self.np_img, self.pbuffer = get_buffer(self.shared, self.settings)

	def render_draw(self):

		if self.frame_info.osr_index >= self.start_index:
			if self.img.size[0] == 1:
				self.img = self.pbuffer

		in_break = check_break(self.beatmap, self.component, self.frame_info, self.updater)
		check_key(self.component, self.cursor_event, in_break)
		add_followpoints(self.beatmap, self.component, self.frame_info, self.preempt_followpoint)
		add_hitobjects(self.beatmap, self.component, self.frame_info, self.time_preempt, self.settings)

		self.updater.update(self.frame_info.cur_time)

		cursor_x = int(self.cursor_event.event[Replays.CURSOR_X] * self.settings.playfieldscale) + self.settings.moveright
		cursor_y = int(self.cursor_event.event[Replays.CURSOR_Y] * self.settings.playfieldscale) + self.settings.movedown

		self.component.background.add_to_frame(self.img, self.np_img, self.frame_info.cur_time, in_break)
		self.component.scorebarbg.add_to_frame(self.img, self.frame_info.cur_time, in_break)
		self.component.timepie.add_to_frame(self.np_img, self.img, self.frame_info.cur_time,self.component.scorebarbg.h,self.component.scorebarbg.alpha, in_break)
		self.component.scorebar.add_to_frame(self.img, self.frame_info.cur_time, in_break)
		self.component.arrowwarning.add_to_frame(self.img, self.frame_info.cur_time)
		self.component.inputoverlayBG.add_to_frame(self.img, self.settings.width - self.component.inputoverlayBG.w() // 2, int(320 * self.settings.scale))
		self.component.urbar.add_to_frame_bar(self.img)
		self.component.key1.add_to_frame(self.img, self.settings.width - int(24 * self.settings.scale), int(350 * self.settings.scale), self.frame_info.cur_time)
		self.component.key2.add_to_frame(self.img, self.settings.width - int(24 * self.settings.scale), int(398 * self.settings.scale), self.frame_info.cur_time)
		self.component.mouse1.add_to_frame(self.img, self.settings.width - int(24 * self.settings.scale), int(446 * self.settings.scale), self.frame_info.cur_time)
		self.component.mouse2.add_to_frame(self.img, self.settings.width - int(24 * self.settings.scale), int(492 * self.settings.scale), self.frame_info.cur_time)
		self.component.followpoints.add_to_frame(self.img, self.frame_info.cur_time)
		self.component.hitobjmanager.add_to_frame(self.img, self.frame_info.cur_time)
		self.component.hitresult.add_to_frame(self.img)
		self.component.spinbonus.add_to_frame(self.img)
		self.component.combocounter.add_to_frame(self.img, in_break)
		self.component.scorecounter.add_to_frame(self.img, self.cursor_event.event[Replays.TIMES], in_break)
		self.component.accuracy.add_to_frame(self.img, in_break)
		self.component.urbar.add_to_frame(self.img)
		self.component.cursor_trail.add_to_frame(self.img, cursor_x, cursor_y, self.cursor_event.event[Replays.TIMES])
		self.component.cursor.add_to_frame(self.img, cursor_x, cursor_y)
		self.component.cursormiddle.add_to_frame(self.img, cursor_x, cursor_y)
		self.component.sections.add_to_frame(self.img)
		self.component.scoreboard.add_to_frame(self.np_img, self.img, in_break)

		self.frame_info.cur_time += self.settings.timeframe / self.settings.fps

		# choose correct osr index for the current time because in osr file there might be some lag
		tt = nearer(self.frame_info.cur_time, self.replay_event, self.frame_info.osr_index)
		if tt == 0:
			self.cursor_event.event = smoothcursor(self.replay_event, self.frame_info.osr_index, self.cursor_event)
		else:
			self.frame_info.osr_index += tt
			self.cursor_event.event = self.replay_event[self.frame_info.osr_index]
		return self.img.size[0] != 1

	def initialiseranking(self):
		self.component.rankingpanel.start_show()
		self.component.rankinghitresults.start_show()
		self.component.rankingtitle.start_show()
		self.component.rankingcombo.start_show()
		self.component.rankingaccuracy.start_show()
		self.component.rankinggrade.start_show()
		self.component.menuback.start_show()
		self.component.modicons.start_show()
		self.component.rankingreplay.start_show()
		self.component.rankinggraph.start_show()

	def draw_rankingpanel(self):
		if not self.initialised_ranking:
			self.initialiseranking()
			self.initialised_ranking = True

		self.component.rankingpanel.add_to_frame(self.pbuffer)
		self.component.rankinghitresults.add_to_frame(self.pbuffer)
		self.component.rankingtitle.add_to_frame(self.pbuffer, self.np_img)
		self.component.rankingcombo.add_to_frame(self.pbuffer)
		self.component.rankingaccuracy.add_to_frame(self.pbuffer)
		self.component.rankinggrade.add_to_frame(self.pbuffer)
		self.component.menuback.add_to_frame(self.pbuffer)
		self.component.modicons.add_to_frame(self.pbuffer)
		self.component.rankingreplay.add_to_frame(self.pbuffer)
		self.component.rankinggraph.add_to_frame(self.pbuffer)


def draw_frame(shared, conn, beatmap, frames, replay_info, resultinfo, videotime, settings, showranking):
	try:
		draw(shared, conn, beatmap, frames, replay_info, resultinfo, videotime, settings, showranking)
	except Exception as e:
		logging.error("{} from {}\n\n\n".format(repr(e), videotime))
		raise


def draw(shared, conn, beatmap, frames, replay_info, resultinfo, videotime, settings, showranking):
	asdfasdf = time.time()

	logging.log(1, "CALL {}, {}".format(videotime, showranking))

	logging.log(logging.DEBUG, "process start")

	drawer = Drawer(shared, beatmap, frames, replay_info, resultinfo, videotime, settings)

	logging.log(1, "PROCESS {}, {}".format(videotime, drawer))

	logging.log(logging.DEBUG, "setup done")
	timer = 0
	timer2 = 0
	timer3 = 0
	while drawer.frame_info.osr_index < videotime[1]:
		status = drawer.render_draw()
		asdf = time.time()
		if status:
			conn.send(1)
			timer3 += time.time() - asdf

			asdf = time.time()
			i = conn.recv()
			timer2 += time.time() - asdf

	if showranking:
		for x in range(int(5 * settings.fps)):
			drawer.draw_rankingpanel()
			conn.send(1)
			i = conn.recv()

	conn.send(10)
	logging.debug("\nprocess done {}, {}".format(videotime, drawer))
	logging.debug("Drawing time: {}".format(timer))
	logging.debug("Total time: {}".format(time.time() - asdfasdf))
	logging.debug("Waiting time: {}".format(timer2))
	logging.debug("Changing value time: {}".format(timer3))
