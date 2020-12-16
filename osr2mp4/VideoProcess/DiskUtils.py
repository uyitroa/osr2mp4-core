import os
import subprocess
import shutil

from osr2mp4 import log_stream


def concat_videos(settings):
	_, file_extension = os.path.splitext(settings.output)
	f = os.path.join(settings.temp, "outputf" + file_extension)
	listvideopath = os.path.abspath(os.path.join(settings.temp, "listvideo.txt")).replace("\\", "/")
	stream = log_stream()
	subprocess.check_call([settings.ffmpeg, '-safe', '0', '-f', 'concat', '-i', listvideopath, '-c', 'copy', f, '-y'], stdout=stream, stderr=stream)


def rename_video(settings):
	_, file_extension = os.path.splitext(settings.output)
	f = os.path.join(settings.temp, "outputf" + file_extension)
	current_file = os.path.join(settings.temp, "output0" + file_extension)
	os.rename(current_file, f)


def cleanup(settings):
	if os.path.isdir(settings.temp):
		shutil.rmtree(settings.temp)
	if os.path.isfile(os.path.join(settings.temp, "listvideo.txt")):
		os.remove(os.path.join(settings.temp, "listvideo.txt"))


def mix_video_audio(settings):
	_, file_extension = os.path.splitext(settings.output)
	f = os.path.join(settings.temp, "outputf" + file_extension)
	stream = log_stream()
	subprocess.check_call([settings.ffmpeg, '-i', f, '-i', settings.temp + 'audio.mp3', '-c:v', 'copy', '-c:a', settings.audiocodec, '-ab', str(settings.settings["Audio bitrate"]) + "k", settings.output, '-y'], stdout=stream, stderr=stream)


def convert_tomp4(settings, output="output.mp4"):
	os.system('"{}" -i "{}" -codec copy {} -y'.format(settings.ffmpeg, settings.output, output))


def setup_dir(settings):
	if not os.path.isdir(settings.temp):
		os.makedirs(settings.temp)
	if not os.path.isdir(os.path.join(settings.path, "logs")):
		# shutil.rmtree(settings.path + "logs")
		os.makedirs(os.path.join(settings.path, "logs"))

	exists = os.path.isfile(os.path.join(settings.temp, "speed.txt"))
	if exists:
		os.remove(os.path.join(settings.temp, "speed.txt"))
