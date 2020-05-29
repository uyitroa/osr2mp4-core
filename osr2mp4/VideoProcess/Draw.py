import time

from ..EEnum.EReplay import Replays
from .smoothing import smoothcursor
from .Setup import setup_global, setup_draw
from .calc import check_break, check_key, add_followpoints, add_hitobjects, nearer
from ..global_var import Settings


def render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
                preempt_followpoint, replay_event, start_index, time_preempt, updater):

	if frame_info.osr_index >= start_index:
		if img.size[0] == 1:
			img = pbuffer


	in_break = check_break(beatmap, component, frame_info, updater)
	check_key(component, cursor_event, in_break)
	add_followpoints(beatmap, component, frame_info, preempt_followpoint)
	add_hitobjects(beatmap, component, frame_info, time_preempt)


	updater.update(frame_info.cur_time)


	cursor_x = int(cursor_event.event[Replays.CURSOR_X] * Settings.playfieldscale) + Settings.moveright
	cursor_y = int(cursor_event.event[Replays.CURSOR_Y] * Settings.playfieldscale) + Settings.movedown


	component.background.add_to_frame(img, np_img, frame_info.cur_time, in_break)
	component.scorebarbg.add_to_frame(img, frame_info.cur_time, in_break)
	component.timepie.add_to_frame(np_img, img, frame_info.cur_time, component.scorebarbg.h, component.scorebarbg.alpha, in_break)
	component.scorebar.add_to_frame(img, frame_info.cur_time, in_break)
	component.arrowwarning.add_to_frame(img, frame_info.cur_time)
	component.inputoverlayBG.add_to_frame(img, Settings.width - component.inputoverlayBG.w() // 2, int(320 * Settings.scale))
	component.urbar.add_to_frame_bar(img)
	component.key1.add_to_frame(img, Settings.width - int(24 * Settings.scale), int(350 * Settings.scale))
	component.key2.add_to_frame(img, Settings.width - int(24 * Settings.scale), int(398 * Settings.scale))
	component.mouse1.add_to_frame(img, Settings.width - int(24 * Settings.scale), int(446 * Settings.scale))
	component.mouse2.add_to_frame(img, Settings.width - int(24 * Settings.scale), int(492 * Settings.scale))
	component.followpoints.add_to_frame(img, frame_info.cur_time)
	component.hitobjmanager.add_to_frame(img, np_img)
	component.hitresult.add_to_frame(img)
	component.spinbonus.add_to_frame(img)
	component.combocounter.add_to_frame(img, in_break)
	component.scorecounter.add_to_frame(img, cursor_event.event[Replays.TIMES], in_break)
	component.accuracy.add_to_frame(img, in_break)
	component.urbar.add_to_frame(img)
	component.cursor_trail.add_to_frame(img, cursor_x, cursor_y, cursor_event.event[Replays.TIMES])
	component.cursor.add_to_frame(img, cursor_x, cursor_y)
	component.cursormiddle.add_to_frame(img, cursor_x, cursor_y)
	component.sections.add_to_frame(img)
	component.scoreboard.add_to_frame(np_img, img, in_break)


	frame_info.cur_time += Settings.timeframe / Settings.fps


	# choose correct osr index for the current time because in osr file there might be some lag
	tt = nearer(frame_info.cur_time, replay_event, frame_info.osr_index)
	if tt == 0:
		cursor_event.event = smoothcursor(replay_event, frame_info.osr_index, cursor_event)
	else:
		frame_info.osr_index += tt
		cursor_event.event = replay_event[frame_info.osr_index]
	return img.size[0] != 1


def draw_frame(shared, conn, beatmap, frames, skin, replay_event, replay_info, resultinfo, start_index, end_index, hd, settings, paths, skinpaths, gameplaysettings, showranking):
	asdfasdf = time.time()
	print("process start")

	setup_global(settings, paths, skinpaths, gameplaysettings)

	component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater = setup_draw(
		beatmap, frames, replay_event, replay_info, resultinfo, shared, skin, start_index, hd)

	print("setup done")
	timer = 0
	timer2 = 0
	timer3 = 0
	while frame_info.osr_index < end_index:
		asdf = time.time()
		status = render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
		                     preempt_followpoint, replay_event, start_index, time_preempt, updater)
		timer += time.time() - asdf

		asdf = time.time()
		if status:
			conn.send(1)
			timer3 += time.time() - asdf

			asdf = time.time()
			i = conn.recv()
			timer2 += time.time() - asdf
		# print("unlocked", timer2)

	if showranking:
		component.rankingpanel.start_show()
		component.rankinghitresults.start_show()
		component.rankingtitle.start_show()
		component.rankingcombo.start_show()
		component.rankingaccuracy.start_show()
		component.rankinggrade.start_show()
		component.menuback.start_show()
		component.modicons.start_show()
		component.rankingreplay.start_show()
		component.rankinggraph.start_show()
		for x in range(int(5 * Settings.fps)):
			# np_img.fill(0)
			component.rankingpanel.add_to_frame(pbuffer)
			component.rankinghitresults.add_to_frame(pbuffer)
			component.rankingtitle.add_to_frame(pbuffer, np_img)
			component.rankingcombo.add_to_frame(pbuffer)
			component.rankingaccuracy.add_to_frame(pbuffer)
			component.rankinggrade.add_to_frame(pbuffer)
			component.menuback.add_to_frame(pbuffer)
			component.modicons.add_to_frame(pbuffer)
			component.rankingreplay.add_to_frame(pbuffer)
			component.rankinggraph.add_to_frame(pbuffer)

			conn.send(1)
			i = conn.recv()

	conn.send(10)
	print("\nprocess done")
	print("Drawing time:", timer)
	print("Total time:", time.time() - asdfasdf)
	print("Waiting time:", timer2)
	print("Changing value time:", timer3)


def draw_rankingpanel():
	pass
