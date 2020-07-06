import logging
import time
import numpy as np
import cv2


def write_frame(shared, conn, filename, settings, iii):
	try:
		write(shared, conn, filename, settings, iii)
	except Exception as e:
		logging.error("{} from {}\n\n\n".format(repr(e), filename))
		raise


def write(shared, conn, filename, settings, iii):
	asdfasdf = time.time()

	logging.log(logging.DEBUG, "{} {} \n".format(filename, vars(settings)))

	writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*settings.codec), settings.fps, (settings.width, settings.height))
	np_img = np.frombuffer(shared, dtype=np.uint8)
	np_img = np_img.reshape((settings.height, settings.width, 4))

	timer = 0

	timer2 = 0
	timer3 = 0
	a = 0
	framecount = 1
	logging.log(logging.DEBUG, "start writing: %f", time.time() - asdfasdf)

	startwringtime = time.time()

	if iii:
		filewriter = open(settings.temp + "speed.txt", "w")

	while a != 10:

		asdf = time.time()
		a = conn.recv()
		timer2 += time.time() - asdf

		if a == 1:
			asdf = time.time()
			im = cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB)
			conn.send(0)
			timer3 += time.time() - asdf

			asdf = time.time()
			writer.write(im)
			timer += time.time() - asdf

			framecount += 1
			if iii and framecount % 200:
				deltatime = max(1, timer)
				filewriter.seek(0)
				logging.log(1, "Writing progress {}, {}, {}, {}".format(framecount, deltatime, filename, startwringtime))
				filewriter.write("{}\n{}\n{}\n{}".format(framecount, deltatime, filename, startwringtime))
				filewriter.truncate()

	if iii:
		filewriter.write("done")
		filewriter.close()

	writer.release()

	logging.debug("\nWriting done {}".format(filename))
	logging.debug("Writing time: {}".format(timer))
	logging.debug("Total time: {}".format(time.time() - asdfasdf))
	logging.debug("Waiting time: {}".format(timer2))
	logging.debug("Changing value time: {}".format(timer3))
