import multiprocessing
from multiprocessing import Pipe, Process
import os
from create_frames import create_frame
from CheckSystem.checkmain import checkmain
from Objects.HitObjects.PrepareHitObjFrames import PrepareCircles, PrepareSlider, PrepareSpinner
from Parser.osuparser import *
from Parser.osrparser import *
from Parser.skinparser import Skin

# const
PATH = "../res/skin8/"
WIDTH = 1280
HEIGHT = 720
FPS = 60
PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT = WIDTH * 0.8 * 3 / 4, HEIGHT * 0.8  # actual playfield is smaller than screen res
PLAYFIELD_SCALE = PLAYFIELD_WIDTH / 512
SCALE = HEIGHT / 768
MOVE_RIGHT = int(WIDTH * 0.2)  # center the playfield
MOVE_DOWN = int(HEIGHT * 0.1)
BEATMAP_FILE = "../res/tengaku.osu"
REPLAY_FILE = "../res/ten.osr"


def divide_core(max_osr, beatmap, skin, replay_event, resultinfo, pcircle, pslider, pspinner):
	cpu_count = multiprocessing.cpu_count()
	frame_processes = cpu_count - 1
	parents_conn, children_conn = [], []
	processes = []
	osr_interval = int(max_osr / frame_processes)

	start_index = 0
	for x in range(frame_processes):
		if x == frame_processes-1:
			end_index = max_osr - start_index
		else:
			end_index = start_index + osr_interval
		p, c = Pipe()
		parents_conn.append(p)
		children_conn.append(c)
		processes.append(Process(target=create_frame, args=(c, beatmap, skin, replay_event, resultinfo, start_index, end_index, pcircle, pslider, pspinner)))
		start_index += osr_interval
	return processes, parents_conn, children_conn


def main():
	writer = cv2.VideoWriter("output.mkv", cv2.VideoWriter_fourcc(*"X264"), FPS, (WIDTH, HEIGHT))
	skin = Skin(PATH)
	beatmap = read_file(BEATMAP_FILE, PLAYFIELD_SCALE, skin.colours)
	replay_event, cur_time = setupReplay(REPLAY_FILE, beatmap.start_time, beatmap.end_time)

	pcircle = PrepareCircles(beatmap, PATH, PLAYFIELD_SCALE, skin)
	pslider = PrepareSlider(PATH, beatmap.diff, PLAYFIELD_SCALE, skin, MOVE_DOWN, MOVE_RIGHT)
	pspinner = PrepareSpinner(PLAYFIELD_SCALE, PATH)


	endtime_fp = beatmap.hitobjects[-1]["time"] + 800
	beatmap.hitobjects.append(
		{"x": 0, "y": 0, "time": endtime_fp, "combo_number": 0, "type": ["end"]})  # to avoid index out of range

	for x in range(10):
		replay_event.append([replay_event[-1][CURSOR_X], replay_event[-1][CURSOR_Y], 0, int(replay_event[-1][TIMES]+1000/FPS)])

	replay_event.append([0, 0, 0, replay_event[-1][3] * 5])
	replay_event.append([0, 0, 0, replay_event[-1][3] * 5])

	resultinfo = checkmain(beatmap, replay_event, cur_time)
	# p, c = Pipe()
	# process = Process(target=create_frame,
	#         args=(c, beatmap, skin, replay_event, resultinfo, 0, 1000, pcircle, pslider, pspinner))
	# process.start()
	# c.close()
	# imgs = p.recv()
	create_frame(beatmap, skin, replay_event, resultinfo, 0, 1000, pcircle, pslider, pspinner)
	#
	# processes, parents_conn, children_conn = divide_core(4000, beatmap, skin, replay_event, resultinfo, pcircle, pslider, pspinner)
	# for x in range(len(processes)):
	# 	processes[x].start()
	# 	children_conn[x].close()
	#
	# for x in range(len(processes)):
	# 	frames = parents_conn[x].recv()
	# 	while len(frames) != 0:
	# 		writer.write(frames[0])
	# 		del frames[0]

	print("setup done")
	writer.release()


if __name__ == "__main__":
	main()
	print("Done Converting..")
	os.system("ffmpeg -i output.mkv -c copy output.mp4 -y")
	os.system("rm output.mkv")
# replay_info = osrparse.parse_replay_file("../res/imaginedragons.osr")
# replay_event = setupReplay(replay_info)
# print(replay_event)
