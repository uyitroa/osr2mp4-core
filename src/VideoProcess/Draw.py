import time

import cv2

from EEnum.EReplay import Replays
from VideoProcess.Setup import setup_global, setup_draw
from VideoProcess.calc import check_break, check_key, add_followpoints, add_hitobjects, nearer
from global_var import Settings


def render_draw(beatmap, component, cursor_event, frame_info, img, np_img, pbuffer,
                preempt_followpoint, replay_event, start_index, time_preempt, updater):

	if frame_info.osr_index >= start_index:
		if img.size[0] == 1:
			img = pbuffer


	in_break = check_break(beatmap, component, frame_info)
	check_key(component, cursor_event, in_break)
	add_followpoints(beatmap, component, frame_info, preempt_followpoint)
	add_hitobjects(beatmap, component, frame_info, time_preempt)


	updater.update(frame_info.cur_time)


	cursor_x = int(cursor_event.event[Replays.CURSOR_X] * Settings.playfieldscale) + Settings.moveright
	cursor_y = int(cursor_event.event[Replays.CURSOR_Y] * Settings.playfieldscale) + Settings.movedown


	component.background.add_to_frame(img, np_img, frame_info.cur_time)
	component.scorebarbg.add_to_frame(img)
	component.scorebar.add_to_frame(img, frame_info.cur_time)
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
	component.combocounter.add_to_frame(img)
	component.scorecounter.add_to_frame(img, cursor_event.event[Replays.TIMES])
	component.accuracy.add_to_frame(img)
	component.urbar.add_to_frame(img)
	component.cursor_trail.add_to_frame(img, cursor_x, cursor_y)
	component.cursor.add_to_frame(img, cursor_x, cursor_y)
	component.cursormiddle.add_to_frame(img, cursor_x, cursor_y)
	component.sections.add_to_frame(img)
	component.timepie.add_to_frame(np_img, frame_info.cur_time)


	frame_info.cur_time += Settings.timeframe / Settings.fps

	# print(cursor_event.event[Replays.CURSOR_X], cursor_event.event[Replays.CURSOR_Y])
	# cv2.putText(np_img, str(cursor_event.event[Replays.CURSOR_X]) + " " + str(cursor_event.event[Replays.CURSOR_Y]), (100, 100),
	#             cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255, 255), 1)


	# choose correct osr index for the current time because in osr file there might be some lag
	frame_info.osr_index += nearer(frame_info.cur_time, replay_event, frame_info.osr_index)
	cursor_event.event = replay_event[frame_info.osr_index]
	return img.size[0] != 1


def draw_frame(shared, conn, beatmap, frames, skin, replay_event, resultinfo, start_index, end_index, hd, settings, paths, skinpaths):
	asdfasdf = time.time()
	print("process start")

	setup_global(settings, paths, skinpaths)

	component, cursor_event, frame_info, img, np_img, pbuffer, preempt_followpoint, time_preempt, updater = setup_draw(
		beatmap, frames, replay_event, resultinfo, shared, skin, start_index, hd)

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
			# print("send")
			conn.send(1)
			# print("sent")
			timer3 += time.time() - asdf

			asdf = time.time()
			# print("wait")
			i = conn.recv()
			# print("received")
			timer2 += time.time() - asdf
		# print("unlocked", timer2)

	conn.send(10)
	print("\nprocess done")
	print("Drawing time:", timer)
	print("Total time:", time.time() - asdfasdf)
	print("Waiting time:", timer2)
	print("Changing value time:", timer3)
