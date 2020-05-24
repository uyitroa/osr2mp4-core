import os
from copy import deepcopy
from multiprocessing import Process
from recordclass import recordclass
from scipy.io.wavfile import write
import numpy as np
from pydub import AudioSegment
from pydub import exceptions
from AudioProcess.AddAudio import HitsoundManager
from AudioProcess.Hitsound import Hitsound
from AudioProcess.Utils import getfilenames, nextpowerof2
from global_var import Paths, SkinPaths, Settings

Audio2p = recordclass("Audio2p", "rate audio")


def read(f, addvolume=0, speed=1.0, changepitch=True):
	if speed != 1.0 and not changepitch:
		os.system('"{}" -i "{}" -codec:a libmp3lame -filter:a "atempo={}" spedup.mp3 -y'.format(Paths.ffmpeg, f, speed))
		f = "spedup.mp3"

	if f[-1] == "3":
		a = AudioSegment.from_mp3(f)
	else:
		a = AudioSegment.from_file(f)
	a += addvolume

	if speed != 1.0:
		if changepitch:
			faster_senpai = a._spawn(a.raw_data, overrides={'frame_rate': int(a.frame_rate * speed)})
			a = faster_senpai.set_frame_rate(a.frame_rate)
	return pydubtonumpy(a)


def pydubtonumpy(audiosegment):
	y = np.array(audiosegment.get_array_of_samples())
	if audiosegment.channels == 2:
		y = y.reshape((-1, 2))
	if audiosegment.channels == 1:
		y1 = np.zeros((len(y), 2), dtype=y.dtype)
		y1[:, 0] = y * 0.5
		y1[:, 1] = y * 0.5
		y = y1

	maxvalue = max(nextpowerof2(np.amax(y)) * 2, 2 ** 16)
	return audiosegment.frame_rate, np.float32(y) / maxvalue


def getaudiofromfile(filename, path, defaultpath, fmt="mp3", addvolume=0, speed=1.0):
	try:
		return read(path + filename + "." + fmt, addvolume=addvolume, speed=speed)
	except FileNotFoundError:
		nxtfmt = "mp3"
		if fmt == "mp3":
			nxtfmt = "wav"

		if defaultpath is not None:
			if fmt == "mp3":
				return getaudiofromfile(filename, path, defaultpath, fmt="wav")
			return getaudiofromfile(filename, defaultpath, None, nxtfmt)

		return 1, np.zeros((0, 2), dtype=np.float32)

	except exceptions.CouldntDecodeError:
		return 1, np.zeros((0, 2), dtype=np.float32)


def getaudiofrombeatmap(filename, beatmappath, path, defaultpath, addvolume=0, speed=1.0):
	try:
		return read(beatmappath + filename + "." + "wav", addvolume=addvolume, speed=speed)
	except FileNotFoundError:
		filename = ''.join(filter(lambda x: not x.isdigit(), filename))
		return getaudiofromfile(filename, path, defaultpath, addvolume=addvolume, speed=speed)
	except exceptions.CouldntDecodeError:
		return 1, np.zeros((0, 2), dtype=np.float32)


def setuphitsound(filenames, beatmappath, skinpath, defaultpath, settings=None):

	bmapindex = 0
	skinindex = 1

	for f in filenames[bmapindex]:
		Hitsound.hitsounds[f] = Audio2p(*getaudiofrombeatmap(f, beatmappath, skinpath, defaultpath))
	for f in filenames[skinindex]:
		Hitsound.hitsounds[f] = Audio2p(*getaudiofromfile(f, skinpath, defaultpath))

	Hitsound.spinnerbonus = Audio2p(*getaudiofromfile("spinnerbonus", skinpath, defaultpath))
	Hitsound.miss = Audio2p(*getaudiofromfile("combobreak", skinpath, defaultpath))
	Hitsound.sectionfail = Audio2p(*getaudiofromfile("sectionfail", skinpath, defaultpath))
	Hitsound.sectionpass = Audio2p(*getaudiofromfile("sectionpass", skinpath, defaultpath))

	for x in range(10, 20):
		speed = x/10
		Hitsound.spinnerspin.append(Audio2p(*getaudiofromfile("spinnerspin", skinpath, defaultpath, speed=speed)))


def getoffset(offset, endtime, song):
	if offset >= 0:
		rendtime = endtime - offset
		out = song.audio[int(offset / 1000 * song.rate):]
	else:
		offset = -offset
		rendtime = endtime + offset
		out = np.zeros((len(song.audio) + int(offset / 1000 * song.rate), 2), dtype=song.audio.dtype)
		out[int(offset / 1000 * song.rate):] = song.audio

	if endtime != -1:
		out = out[:int(rendtime / 1000 * song.rate)]

	return out


def processaudio(my_info, beatmap, skin_path, offset, endtime, default_skinpath, beatmap_path, audio_name, dt):
	song = Audio2p(*read(beatmap_path + audio_name, addvolume=-10, speed=Settings.timeframe/1000, changepitch=not dt))
	song.rate /= Settings.timeframe/1000

	filenames = getfilenames(beatmap)
	setuphitsound(filenames, beatmap_path, skin_path, default_skinpath)

	hitsoundm = HitsoundManager(beatmap)

	for x in range(len(my_info)):

		hitsoundm.updatetimingpoint(my_info, x, song)
		hitsoundm.addhitsound(my_info, x, song)
		hitsoundm.addslidersound(my_info, x, song)
		hitsoundm.addspinnerhitsound(my_info, x, song)
		hitsoundm.addcombobreak(my_info, x, song)
		hitsoundm.addsectionsound(my_info, x, song)

	out = getoffset(offset, endtime, song)

	write('audio.mp3', round(song.rate * Settings.timeframe/1000), out)



def create_audio(my_info, beatmap_info, offset, endtime, audio_name, mpp, dt):
	beatmap_path = Paths.beatmap
	default_skinP = SkinPaths.default_path
	skin_path = SkinPaths.path

	beatmap_info = deepcopy(beatmap_info)

	if mpp >= 1:
		audio_args = (my_info, beatmap_info, skin_path, offset, endtime, default_skinP, beatmap_path, audio_name, dt,)
		audio = Process(target=processaudio, args=audio_args)
		audio.start()
		return audio
	else:
		processaudio(my_info, beatmap_info, skin_path, offset, endtime, default_skinP, beatmap_path, audio_name, dt)
		return None
