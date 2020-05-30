import os
import subprocess
import shutil
from ..global_var import Paths


def concat_videos():
	f = Paths.temp + "outputf" + Paths.output[-4:]
	# command = '"{}" -safe 0 -f concat -i ../temp/listvideo.txt -c copy "{}" -y'.format(Paths.ffmpeg, f)
	# if os.name == 'nt':
	# 	command = '"' + command + '"'
	# os.system(command)
	subprocess.call([Paths.ffmpeg, '-safe', '0', '-f', 'concat', '-i', Paths.temp + 'listvideo.txt', '-c', 'copy', f, '-y'])


def cleanup():
	if os.path.isdir(Paths.temp):
		shutil.rmtree(Paths.temp)
	if os.path.isfile(Paths.temp + "listvideo.txt"):
		os.remove(Paths.temp + "listvideo.txt")


def mix_video_audio():
	f = Paths.temp + "outputf" + Paths.output[-4:]
	# command = '"{}" -i "{}" -i ../temp/audio.mp3 -c:v copy -c:a aac "{}" -y'.format(Paths.ffmpeg, f, Paths.output)
	# if os.name == 'nt':
	# 	command = '"' + command + '"'
	#
	# os.system(command)
	subprocess.call([Paths.ffmpeg, '-i', f, '-i', Paths.temp + 'audio.mp3', '-c:v', 'copy', '-c:a', 'aac', Paths.output, '-y'])


def convert_tomp4():
	os.system('"{}" -i "{}" -codec copy output.mp4 -y'.format(Paths.ffmpeg, Paths.output))


def setup_dir():
	if not os.path.isdir(Paths.temp):
		os.makedirs(Paths.temp)
	if not os.path.isdir(Paths.path + "logs"):
		os.makedirs(Paths.path + "logs")

	exists = os.path.isfile(Paths.temp + "speed.txt")
	if exists:
		os.remove(Paths.temp + "speed.txt")
