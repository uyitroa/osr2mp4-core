import os
import time
import traceback
import numpy as np
import math
import cv2
from pathlib import Path
from osr2mp4 import logger
from osr2mp4.global_var import videoextensions
from osr2mp4.Exceptions import CannotCreateVideo, FourccIsNotExtension, WrongFourcc, LibAvNotFound

### TODO: MOVE THIS TO ITS OWN FILE
def equal(n: int):
    return [1/n]*n

def pyramid(n: int):
    val = [x/n for x in np.arange(1, n+1)]
    val /= np.sum(val)
    return val

def gauss(n: int):
    val = [math.exp(-(1.5*x/n)**2) for x in np.arange(n, 0, -1)]
    val /= np.sum(val)
    return val

def blending(imgs: list):
	weight = equal(len(imgs))
	p = np.einsum("ijkl,i->jkl", imgs, weight)
	return p.astype(np.uint8)

###

def write_frame(shared: object, conn: object, filename: Path, settings: dict, iii: bool):
	try:
		write(shared, conn, filename, settings, iii)
	except Exception as e:
		tb = traceback.format_exc()
		with open("error.txt", "w") as fwrite:  # temporary fix
			fwrite.write(repr(e))
		logger.error("{} from {}\n{}\n\n\n".format(tb, filename, repr(e)))
		raise


def getwriter(filename: Path, settings: dict, buf: object):
	videoerror = None
	if not settings.settings["Use FFmpeg video writer"]:
		if len(settings.codec) != 4:
			raise WrongFourcc()

		writer = cv2.VideoWriter(str(filename), cv2.VideoWriter_fourcc(*settings.codec), settings.video_fps, (settings.width, settings.height))
	else:
		try:
			from osr2mp4.VideoProcess.FFmpegWriter.osr2mp4cv import PyFrameWriter
		except ImportError as e:
			raise LibAvNotFound

		if settings.settings["FFmpeg codec"] == "":
			settings.settings["FFmpeg codec"] = "libx264"
			
		ffmpegcodec = str.encode(settings.settings["FFmpeg codec"])
		ffmpegargs = str.encode(settings.settings["FFmpeg custom commands"])
		writer = PyFrameWriter(str.encode(filename), ffmpegcodec, settings.video_fps, settings.width, settings.height, ffmpegargs, buf)

		try:
			videoerror = writer.geterror().decode()
		except UnicodeDecodeError:
			pass

	if not writer.isOpened():
		raise CannotCreateVideo(msg=videoerror)
	return writer


def write(shared: object, conn: object, filename: Path, settings: dict, iii: bool):
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
	framecount = 0
	logger.debug("start writing: %f", time.time() - asdfasdf)

	startwringtime = time.time()

	if iii:
		filewriter = open(os.path.join(settings.temp, "speed.txt"), "w")

	# GOD HERE WE GO AGAIN
	fps_ratio: int = int(settings.fps / 60)
	frames: list = []
	on_first_frame: bool = True
	start, end = 0, 0
	samples: int = settings.resample_frame
	
	while a != 10:

		asdf = time.time()
		a = conn.recv()
		timer2 += time.time() - asdf

		if a == 1:
			asdf = time.time()
			timer3 += time.time() - asdf
			asdf = time.time()

			if settings.resample:
				start_offset, end_offset = [(samples-1, samples), (0, samples)][on_first_frame]
				# HACK: this whole resample code thing is a hack (or maybe its not)
				#       either way its looks fucking terrible. someone pls fix this
				#       - FireRedz
				if end == 0:
					end = (framecount + end_offset) * fps_ratio

				frames += [np_img.copy()]

				if (framecount + start_offset) * fps_ratio >= end and len(frames) >= fps_ratio:
					final = blending(frames)
					del frames[:fps_ratio]
					cv2.cvtColor(final, cv2.COLOR_BGRA2RGB, dst=buf)
					
					if not settings.settings["Use FFmpeg video writer"]:
						writer.write(buf)
					else:
						writer.write()

					end = 0
					on_first_frame = False
			else:
				cv2.cvtColor(np_img, cv2.COLOR_BGRA2RGB, dst=buf)

				if not settings.settings["Use FFmpeg video writer"]:
					writer.write(buf)
				else:
					writer.write()

			timer += time.time() - asdf

			framecount += 1
			if iii and framecount % 200:
				deltatime = max(1, timer)
				filewriter.seek(0)
				# logger.log(1, "Writing progress {}, {}, {}, {}".format(framecount, deltatime, filename, startwringtime))
				filewriter.write("{}\n{}\n{}\n{}".format(framecount, deltatime, filename, startwringtime))
				filewriter.truncate()

			conn.send(0)

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
