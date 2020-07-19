import os
import subprocess
import shutil


def concat_videos(settings):
	_, file_extension = os.path.splitext(settings.output)
	f = settings.temp + "outputf" + file_extension
	listvideopath = os.path.abspath(os.path.join(settings.temp, "listvideo.txt")).replace("\\", "/")
	subprocess.check_call([settings.ffmpeg, '-safe', '0', '-f', 'concat', '-i', listvideopath, '-c', 'copy', f, '-y'])


def cleanup(settings):
	if os.path.isdir(settings.temp):
		shutil.rmtree(settings.temp)
	if os.path.isfile(settings.temp + "listvideo.txt"):
		os.remove(settings.temp + "listvideo.txt")


def mix_video_audio(settings):
	_, file_extension = os.path.splitext(settings.output)
	f = settings.temp + "outputf" + file_extension
	subprocess.check_call([settings.ffmpeg, '-i', f, '-i', settings.temp + 'audio.mp3', '-c:v', 'copy', '-c:a', 'aac', settings.output, '-y'])


def convert_tomp4(settings, output="output.mp4"):
	os.system('"{}" -i "{}" -codec copy {} -y'.format(settings.ffmpeg, settings.output, output))


def setup_dir(settings):
	if not os.path.isdir(settings.temp):
		os.makedirs(settings.temp)
	if not os.path.isdir(settings.path + "logs"):
		# shutil.rmtree(settings.path + "logs")
		os.makedirs(settings.path + "logs")

	exists = os.path.isfile(settings.temp + "speed.txt")
	if exists:
		os.remove(settings.temp + "speed.txt")
