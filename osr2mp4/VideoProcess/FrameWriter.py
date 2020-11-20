import os
import time
import traceback
import numpy as np
import cv2
from osr2mp4 import logger
from osr2mp4.global_var import videoextensions
from osr2mp4.Exceptions import CannotCreateVideo, FourccIsNotExtension, WrongFourcc, LibAvNotFound
from osr2mp4 import log_stream


def write_frame(shared, conn, filename, settings, iii):
	try:
		write(shared, conn, filename, settings, iii)
	except Exception as e:
		tb = traceback.format_exc()
		with open("error.txt", "w") as fwrite:  # temporary fix
			fwrite.write(repr(e))
		logger.error("{} from {}\n{}\n\n\n".format(tb, filename, repr(e)))
		raise


def getwriter(filename, settings, buf):
	videoerror = None
	if not settings.settings["Use FFmpeg video writer"]:
		if len(settings.codec) != 4:
			raise WrongFourcc()

		writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*settings.codec), settings.fps, (settings.width, settings.height))
	else:
		from osr2mp4.VideoProcess.FFMpegWriter import FFMpegWriter
		if settings.settings["FFmpeg codec"] == "":
			settings.settings["FFmpeg codec"] = "libx264"
		ffmpegcodec = settings.settings["FFmpeg codec"]
		ffmpegargs = settings.settings["FFmpeg custom commands"]
		writer = FFMpegWriter(settings.ffmpeg, settings.output, (settings.width, settings.height), settings.fps, ffmpegcodec, 
			settings.temp + 'audio.mp3', settings.audiocodec, "ultrafast", str(settings.settings["Audio bitrate"]) + "k", 
			logfile = log_stream(), threads = 0,  pixel_format = "bgr24")

	return writer


def write(shared, conn, filename, settings, iii):
	asdfasdf = time.time()

	logger.debug("{}\n".format(filename))
	logger.debug("Start write")

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
	logger.debug("start writing: %f", time.time() - asdfasdf)

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
				writer.write_frame(buf)

			timer += time.time() - asdf

			framecount += 1
			if iii and framecount % 200:
				deltatime = max(1, timer)
				filewriter.seek(0)
				# logger.log(1, "Writing progress {}, {}, {}, {}".format(framecount, deltatime, filename, startwringtime))
				filewriter.write("{}\n{}\n{}\n{}".format(framecount, deltatime, filename, startwringtime))
				filewriter.truncate()

	if iii:
		filewriter.write("done")
		filewriter.close()

	logger.debug("Release write")
	writer.release()

	logger.debug("End write")

	logger.debug("\nWriting done {}".format(filename))
	logger.debug("Writing time: {}".format(timer))
	logger.debug("Total time: {}".format(time.time() - asdfasdf))
	logger.debug("Waiting time: {}".format(timer2))
	logger.debug("Changing value time: {}".format(timer3))
