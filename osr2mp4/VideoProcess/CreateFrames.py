import cv2
from multiprocessing import Process, Pipe
from osr2mp4 import logger
from osr2mp4.VideoProcess.Draw import Drawer
from osr2mp4.VideoProcess.FrameWriter import getwriter
from osr2mp4.VideoProcess.AFrames import PreparedFrames
from osr2mp4.CheckSystem.mathhelper import getunstablerate
import numpy as np
import os

def create_frame(settings, beatmap, replay_info, resultinfo, videotime):
	logger.debug('entering preparedframes')

	logger.debug("process start")

	ur = getunstablerate(resultinfo)
	frames = PreparedFrames(settings, beatmap.diff, replay_info.mod_combination, ur=ur, bg=beatmap.bg)

	shared = np.zeros((settings.height * settings.width * 4), dtype=np.uint8)
	drawer = Drawer(shared, beatmap, frames, replay_info, resultinfo, videotime, settings)

	_, file_extension = os.path.splitext(settings.output)
	f = os.path.join(settings.temp, "outputf" + file_extension)

	writer = getwriter(f, settings)
	buf = np.zeros((settings.height + int(settings.height/2.0), settings.width), dtype=np.uint8)

	logger.debug("setup done")
	startwritetime = time.time()

	while drawer.frame_info.osr_index < videotime[1]:
		status = drawer.render_draw()
		if status:
			cv2.cvtColor(drawer.np_img, cv2.COLOR_BGRA2YUV_YV12, dst=buf)
			writer.write_frame(buf)

	writer.release()
	logger.debug("\nprocess done")

	return None, None, None, None


def create_frame_dual(settings, beatmap, replay_info, resultinfo, videotime):

	_, file_extension = os.path.splitext(settings.output)
	f = os.path.join(settings.temp, "outputf" + file_extension)

	writer_conn, drawer_conn = Pipe(duplex=False)
	drawer = Process(target=draw_frame, args=(drawer_conn, beatmap, replay_info, resultinfo, videotime, settings))
	writer = Process(target=write_frame, args=(writer_conn, f, settings))

	drawer.start()
	writer.start()
	drawer.join()
	writer.join()

	writer_conn.close()
	drawer_conn.close()
	return None, None, None, None

def draw_frame(conn, beatmap, replay_info, resultinfo, videotime, settings):
	try:
		draw(conn, beatmap, replay_info, resultinfo, videotime, settings)
	except Exception as e:
		tb = traceback.format_exc()
		logger.error("{} from {}\n{}\n\n\n".format(tb, videotime, repr(e)))
		raise

def draw(conn, beatmap, replay_info, resultinfo, videotime, settings):
	logger.info("start drawing")

	ur = getunstablerate(resultinfo)
	frames = PreparedFrames(settings, beatmap.diff, replay_info.mod_combination, ur=ur, bg=beatmap.bg)

	shared = np.zeros((settings.height * settings.width * 4), dtype=np.uint8)
	drawer = Drawer(shared, beatmap, frames, replay_info, resultinfo, videotime, settings)
	packed_image = np.zeros((settings.height + int(settings.height/2.0), settings.width), dtype=np.uint8)

	while drawer.frame_info.osr_index < videotime[1]:
		status = drawer.render_draw()
		if status:
			cv2.cvtColor(drawer.np_img, cv2.COLOR_BGRA2YUV_YV12, dst=packed_image)
			conn.send(packed_image.tobytes())
	conn.send(os.EX_OK)

def write_frame(conn, filename, settings):
	try:
		write(conn, filename, settings)
	except Exception as e:
		tb = traceback.format_exc()
		logger.error("{} from {}\n{}\n\n\n".format(tb, filename, repr(e)))
		raise

def write(conn, filename, settings):
	logger.info("Start writing")

	writer = getwriter(filename, settings)

	frame = -1
	while frame != os.EX_OK:
		frame = conn.recv()
		if frame != os.EX_OK:
			writer.write_frame(frame)
		else:
			break

	writer.release()