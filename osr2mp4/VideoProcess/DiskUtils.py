import os
import subprocess

from ..global_var import Paths


def concat_videos():
	f = Paths.path + "temp/outputf" + Paths.output[-4:]
	# command = '"{}" -safe 0 -f concat -i ../temp/listvideo.txt -c copy "{}" -y'.format(Paths.ffmpeg, f)
	# if os.name == 'nt':
	# 	command = '"' + command + '"'
	# os.system(command)
	subprocess.call([Paths.ffmpeg, '-safe', '0', '-f', 'concat', '-i', 'listvideo.txt', '-c', 'copy', f, '-y'])


def cleanup():
	if os.name == 'nt':
		rm_command = "del"
	else:
		rm_command = "rm"

	try:
		subprocess.call([rm_command, Paths.path + "temp/*"])
	except FileNotFoundError:
		pass
	#
	# f = Paths.output[:-4] + "f" + Paths.output[-4:]
	# os.system('{} "{}"'.format(rm_command, f))
	# os.system('{} audio.mp3'.format(rm_command))


def mix_video_audio():
	f = Paths.path + "temp/outputf" + Paths.output[-4:]
	# command = '"{}" -i "{}" -i ../temp/audio.mp3 -c:v copy -c:a aac "{}" -y'.format(Paths.ffmpeg, f, Paths.output)
	# if os.name == 'nt':
	# 	command = '"' + command + '"'
	#
	# os.system(command)
	subprocess.call([Paths.ffmpeg, '-i', f, '-i', Paths.path + 'temp/audio.mp3', '-c:v', 'copy', '-c:a', 'aac', Paths.output, '-y'])


def convert_tomp4():
	os.system('"{}" -i "{}" -codec copy output.mp4 -y'.format(Paths.ffmpeg, Paths.output))


def create_dir():
	if not os.path.isdir(Paths.path + "temp"):
		os.makedirs(Paths.path + "temp")
	if not os.path.isdir(Paths.path + "logs"):
		os.makedirs(Paths.path + "logs")
