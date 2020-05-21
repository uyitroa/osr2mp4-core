from multiprocessing import Process
from recordclass import recordclass
from scipy.io.wavfile import write
import numpy as np
from pydub import AudioSegment
from pydub import exceptions
from AudioProcess.AddAudio import HitsoundManager
from AudioProcess.Hitsound import Hitsound

Audio2p = recordclass("Audio2p", "rate audio")


def read(f, addvolume=0, speed=1.0, changepitch=True):
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
		y1[:, 0] = y
		y1[:, 1] = y
		y = y1
	return audiosegment.frame_rate, np.float32(y) / 2 ** (audiosegment.sample_width * 8 - 1)


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


def setup(skinpath, defaultpath, audiopath, settings=None):

	song = Audio2p(*read(audiopath, addvolume=-10))
	Hitsound.normalhitnormal = Audio2p(*getaudiofromfile("normal-hitnormal", skinpath, defaultpath))
	Hitsound.miss = Audio2p(*getaudiofromfile("combobreak", skinpath, defaultpath))
	Hitsound.spinnerbonus = Audio2p(*getaudiofromfile("spinnerbonus", skinpath, defaultpath))
	Hitsound.normalslidertick = Audio2p(*getaudiofromfile("normal-slidertick", skinpath, defaultpath))

	for x in range(10, 20):
		speed = x/10
		Hitsound.spinnerspin.append(Audio2p(*getaudiofromfile("spinnerspin", skinpath, defaultpath, speed=speed)))

	return song


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


def processaudio(my_info, beatmap, skin_path, offset, endtime, default_skinpath, beatmap_path, audio_name):
	song = setup(skin_path, default_skinpath, beatmap_path + audio_name)

	hitsoundm = HitsoundManager(beatmap)

	for x in range(len(my_info)):

		hitsoundm.addhitsound(my_info, x, song)
		hitsoundm.addslidersound(my_info, x, song)
		hitsoundm.addspinnerhitsound(my_info, x, song)
		hitsoundm.addcombobreak(my_info, x, song)


	out = getoffset(offset, endtime, song)

	write('audio.mp3', song.rate, out)



def create_audio(my_info, beatmap_info, offset, endtime, audio_name, mpp):
	from global_var import Paths, SkinPaths
	beatmap_path = Paths.beatmap
	default_skinP = SkinPaths.default_path
	skin_path = SkinPaths.path

	if mpp >= 1:
		audio_args = (my_info, beatmap_info, skin_path, offset, endtime, default_skinP, beatmap_path, audio_name,)
		audio = Process(target=processaudio, args=audio_args)
		audio.start()
		return audio
	else:
		processaudio(my_info, beatmap_info, skin_path, offset, endtime, default_skinP, beatmap_path, audio_name)
		return None
