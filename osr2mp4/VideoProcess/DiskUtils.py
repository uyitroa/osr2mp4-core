import os
import subprocess
import shutil

from osr2mp4 import log_stream


def concat_videos(settings: object):
	f = str(settings.temp / ("outputf" + settings.output.suffix))
	listvideopath = (settings.temp / "listvideo.txt").absolute().replace("\\", "/")
	stream = log_stream()
	subprocess.check_call([settings.ffmpeg, '-safe', '0', '-f', 'concat', '-i', listvideopath, '-c', 'copy', f, '-y'], stdout=stream, stderr=stream)


def rename_video(settings: object):
	f = settings.temp / ("outputf" + settings.output.suffix)
	current_file = settings.temp / ("output0" + settings.output.suffix)
	current_file.rename(f)


def cleanup(settings: object):
	if settings.temp.exists():
		# ok pathlib
		shutil.rmtree(settings.temp)

def mix_video_audio(settings: object):
	f = str(settings.temp / ("outputf" + settings.output.suffix))
	stream = log_stream()
	subprocess.check_call([settings.ffmpeg, '-i', f, '-i', str(settings.temp / 'audio.mp3'), '-c:v', 'copy', '-c:a', settings.audiocodec, '-ab', str(settings.settings["Audio bitrate"]) + "k", settings.output, '-y'], stdout=stream, stderr=stream)


def convert_tomp4(settings: object, output: str = "output.mp4"):
	os.system('"{}" -i "{}" -codec copy {} -y'.format(settings.ffmpeg, settings.output, output))


def setup_dir(settings: object):
	if not settings.temp.exists():
		settings.temp.mkdir()

	logs_folder = settings.path / 'logs'
	if not logs_folder.exists():
		logs_folder.mkdir()

	speed_f = settings.temp / "speed.txt"

	if speed_f.exists():
		speed_f.unlink()
