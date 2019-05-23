import os
import cv2
from draw_frames import Frames

# const
PATH = "../res/skin2/"
WIDTH = 1920
HEIGHT = 1080
FPS = 60

def main():
	my_frame = Frames()
	my_frame.prepare_frame()


if __name__ == "__main__":
	main()
	print("Done Converting..")
	os.system("ffmpeg -i output.mkv -c copy output.mp4 -y")
# replay_info = osrparse.parse_replay_file("../res/imaginedragons.osr")
# replay_event = setupReplay(replay_info)
# print(replay_event)
