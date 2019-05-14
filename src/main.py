import os
import cv2
from multiprocessing import Queue, Process
from draw_frames import Frames

# const
PATH = "../res/skin2/"
WIDTH = 1920
HEIGHT = 1080
FPS = 60

def prepare_frame(frame_queue):
	my_frame = Frames()
	my_frame.prepare_frame(frame_queue)

def prepare_write(frame_queue, process):
	writer = cv2.VideoWriter("output.mkv", cv2.VideoWriter_fourcc(*"X264"), FPS, (WIDTH, HEIGHT))
	queue_index = 0
	while not frame_queue.empty or process.is_alive():
		img = frame_queue.get()
		queue_index += 1
		print(queue_index)
		writer.write(img)
	writer.release()

def main():
	queue = Queue()
	process = Process(target=prepare_frame, args=(queue,))
	process.start()
	prepare_write(queue, process)
	process.join()

if __name__ == "__main__":
	main()
	print("Done Converting..")
	os.system("ffmpeg -i output.mkv -c copy output.mp4 -y")
# replay_info = osrparse.parse_replay_file("../res/imaginedragons.osr")
# replay_event = setupReplay(replay_info)
# print(replay_event)
