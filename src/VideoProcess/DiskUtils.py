import os

from global_var import Paths


def concat_videos():
	f = Paths.output[:-4] + "f" + Paths.output[-4:]
	command = '"{}" -safe 0 -f concat -i listvideo.txt -c copy "{}" -y'.format(Paths.ffmpeg, f)
	if os.name == 'nt':
		command = '"' + command + '"'
	os.system(command)


def cleanup():
	if os.name == 'nt':
		rm_command = "del"
	else:
		rm_command = "rm"

	mpp = len(open("listvideo.txt", "r").read().split("\n"))

	os.system('{} listvideo.txt'.format(rm_command))
	for i in range(mpp):
		f = Paths.output[:-4] + str(i) + Paths.output[-4:]
		os.system('{} "{}"'.format(rm_command, f))

	f = Paths.output[:-4] + "f" + Paths.output[-4:]
	os.system('{} "{}"'.format(rm_command, f))
	os.system('{} z.mp3'.format(rm_command))


def mix_video_audio():
	f = Paths.output[:-4] + "f" + Paths.output[-4:]
	command = '"{}" -i "{}" -i z.mp3 -c:v copy -c:a aac "{}" -y'.format(Paths.ffmpeg, f, Paths.output)
	if os.name == 'nt':
		command = '"' + command + '"'

	os.system(command)


def convert_tomp4():
	os.system('"{}" -i "{}" -codec copy output.mp4 -y'.format(Paths.ffmpeg, Paths.output))
