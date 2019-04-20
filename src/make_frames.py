import osrparse
import numpy as np
import cv2
from Components import *


def main():
	width, height = 1920, 1080

	img = np.zeros((height, width, 3)).astype('uint8') # setup background

	replay_info = osrparse.parse_replay_file("../res/kys.osr")
	replay_event = replay_info.play_data

	cursor = Cursor("../res/skin/cursor.png")
	filename = "frame"
	index = 1
	formatte = ".jpg"
	for i in range(len(replay_event)):
		cursor_x = int(replay_event[i].x + 500)
		cursor_y = int(replay_event[i].y + 100)
		cursor.add_to_frame(img, cursor_x, cursor_y)
		cv2.imwrite(filename + str(index) + formatte, img)
		cursor.reset_frame(img)
		index += 1


main()