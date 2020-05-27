import time
import numpy as np
import cv2

from .Setup import setup_global
from ..global_var import Settings


def write_frame(shared, conn, filename, codec, settings, paths, skinpaths, gameplaysettings):
	asdfasdf = time.time()

	setup_global(settings, paths, skinpaths, gameplaysettings)

	writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*codec), Settings.fps, (Settings.width, Settings.height))
	np_img = np.frombuffer(shared, dtype=np.uint8)
	np_img = np_img.reshape((Settings.height, Settings.width, 4))

	timer = 0

	timer2 = 0
	timer3 = 0
	timer4 = 0
	a = 0
	print("start writing:", time.time() - asdfasdf)

	while a != 10:

		asdf = time.time()
		# print("video wait")
		# print(filename)
		a = conn.recv()
		# print("video received")
		timer2 += time.time() - asdf

		if a == 1:

			asdf = time.time()
			im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
			# print("video send")
			conn.send(0)
			# print("video sent")
			timer3 += time.time() - asdf
			# print("unlock", timer3)

			asdf = time.time()
			writer.write(im)
			timer += time.time() - asdf

	writer.release()
	print("\nWriting time:", timer)

	print("\nTotal time:", time.time() - asdfasdf)
	print("Writing time:", timer)
	print("Waiting time:", timer2)
	print("Changing value time:", timer3)
	print("??? value time:", timer4)
