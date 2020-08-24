import logging
import os
import time
import traceback
import numpy as np
import cv2
from osr2mp4.global_var import videoextensions
from osr2mp4.Exceptions import CannotCreateVideo, FourccIsNotExtension, WrongFourcc, LibAvNotFound


def write_frame(shared, conn, filename, settings, iii):
	try:
		write(shared, conn, filename, settings, iii)
	except Exception as e:
		tb = traceback.format_exc()
		with open("error.txt", "w") as fwrite:  # temporary fix
			fwrite.write(repr(e))
		logging.error("{} from {}\n{}\n\n\n".format(tb, filename, repr(e)))
		raise


def getwriter(filename, settings, buf):
	videoerror = None
	if not settings.settings["Use FFmpeg video writer"]:
		if len(settings.codec) != 4:
			raise WrongFourcc()

		writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*settings.codec), settings.fps, (settings.width, settings.height))
	else:
		try:
			from osr2mp4.VideoProcess.FFmpegWriter.osr2mp4cv import PyFrameWriter
		except ImportError as e:
			raise LibAvNotFound
		if settings.settings["FFmpeg codec"] == "":
			settings.settings["FFmpeg codec"] = "libx264"
		ffmpegcodec = str.encode(settings.settings["FFmpeg codec"])
		ffmpegargs = str.encode(settings.settings["FFmpeg custom commands"])
		writer = PyFrameWriter(str.encode(filename), ffmpegcodec, settings.fps, settings.width, settings.height, ffmpegargs, buf)

		try:
			videoerror = writer.geterror().decode()
		except UnicodeDecodeError:
			pass

	if not writer.isOpened():
		raise CannotCreateVideo(msg=videoerror)
	return writer


def write(shared, conn, filename, settings, iii):
	asdfasdf = time.time()

	logging.log(logging.DEBUG, "{}\n".format(filename))
	print("Start write")

	if settings.codec.lower() in videoextensions:
		raise FourccIsNotExtension()

	buf = np.zeros((settings.height * settings.width * 3), dtype=np.uint8)
	writer = getwriter(filename, settings, buf)

	np_img = np.frombuffer(shared, dtype=np.uint8)
	np_img = np_img.reshape((settings.height, settings.width, 4))
	buf = buf.reshape((settings.height, settings.width, 3))

	timer = 0

	timer2 = 0
	timer3 = 0
	a = 0
	framecount = 1
	logging.log(logging.DEBUG, "start writing: %f", time.time() - asdfasdf)

	startwringtime = time.time()

	if iii:
		filewriter = open(os.path.join(settings.temp, "speed.txt"), "w")

	while a != 10:

		asdf = time.time()
		a = conn.recv()
		timer2 += time.time() - asdf

		if a == 1:
			asdf = time.time()
			cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB, dst=buf)
			conn.send(0)
			timer3 += time.time() - asdf

			asdf = time.time()

			if not settings.settings["Use FFmpeg video writer"]:
				writer.write(buf)
			else:
				writer.write()

			timer += time.time() - asdf

			framecount += 1
			if iii and framecount % 200:
				deltatime = max(1, timer)
				filewriter.seek(0)
				# logging.log(1, "Writing progress {}, {}, {}, {}".format(framecount, deltatime, filename, startwringtime))
				filewriter.write("{}\n{}\n{}\n{}".format(framecount, deltatime, filename, startwringtime))
				filewriter.truncate()

	if iii:
		filewriter.write("done")
		filewriter.close()

	print("Release write")
	writer.release()

	print("End write")

	logging.debug("\nWriting done {}".format(filename))
	logging.debug("Writing time: {}".format(timer))
	logging.debug("Total time: {}".format(time.time() - asdfasdf))
	logging.debug("Waiting time: {}".format(timer2))
	logging.debug("Changing value time: {}".format(timer3))
