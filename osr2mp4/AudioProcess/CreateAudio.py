import logging
import math
import os
import subprocess
import time
from copy import deepcopy
from multiprocessing import Process
from osr2mp4.Exceptions import AudioNotFound
from osr2mp4.osrparse.enums import Mod
from recordclass import recordclass
from scipy.io.wavfile import write
import numpy as np
from pydub import AudioSegment
from pydub import exceptions
from osr2mp4.AudioProcess.AddAudio import HitsoundManager
from osr2mp4.AudioProcess.Hitsound import Hitsound
from osr2mp4.AudioProcess.Utils import getfilenames
import os.path


Audio2p = recordclass("Audio2p", "rate audio")


def from_notwav(filename, settings):
	if not os.path.isfile(filename):
		raise FileNotFoundError

	with open(os.path.join(settings.temp, "convert.log"), "a") as cc:
		subprocess.call([settings.ffmpeg, '-i', filename, settings.temp + 'converted.wav', '-y'], stdout=cc, stderr=cc)

	a = AudioSegment.from_file(settings.temp + 'converted.wav')
	return a


def read(f, settings, volume=1.0, speed=1.0, changepitch=True):
	if speed != 1.0 and not changepitch:
		with open(os.path.join(settings.path, "speedup.log"), "a") as cc:
			subprocess.call([settings.ffmpeg, '-i', f, '-codec:a', 'libmp3lame', '-filter:a', 'atempo={}'.format(speed), settings.temp + 'spedup.mp3', '-y'], stdout=cc, stderr=cc)

		f = os.path.join(settings.temp, "spedup.mp3")

	if f[-4:] != ".wav":
		a = from_notwav(f, settings)
	else:
		a = AudioSegment.from_file(f)

	if volume > 0:
		addvolume = 30 * math.log(volume, 10)
		a += addvolume
	else:
		a = AudioSegment.silent(duration=a.duration_seconds * 1000, frame_rate=a.frame_rate)

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
	try:
		h = max(2, audiosegment.sample_width) * 8
		maxvalue = max(np.amax(y), 2 ** h)
	except ValueError as e:
		print(repr(e))
		maxvalue = 1
	return audiosegment.frame_rate, np.float64(y) / maxvalue


def getaudiofromfile(filename, path, defaultpath, settings, volume=1.0, speed=1.0):
	fmts = ["wav", "mp3", "ogg"]
	for fmt in fmts:
		try:
			return read(os.path.join(path, filename + "." + fmt), settings, volume=volume, speed=speed)
		except FileNotFoundError:
			pass

		except exceptions.CouldntDecodeError as e:
			logging.error(repr(e) + " filename " + os.path.join(path, filename + "." + fmt))
			print(repr(e) + " filename " + os.path.join(path, filename + "." + fmt))
			return 1, np.zeros((0, 2), dtype=np.float32)

	print("file not found",  filename, "using default skin")

	if defaultpath is not None:
		return getaudiofromfile(filename, defaultpath, None, settings, volume=volume, speed=speed)

	print("file not found" + filename)
	logging.error("file not found " + filename)
	return 1, np.zeros((0, 2), dtype=np.float32)


def getaudiofrombeatmap(filename, beatmappath, path, defaultpath, settings, volume=1.0, speed=1.0):
	try:
		return read(os.path.join(beatmappath,filename + "." + "wav"), settings, volume=volume, speed=speed)
	except FileNotFoundError:
		try:
			return read(os.path.join(beatmappath, filename + "." + "ogg"), settings, volume=volume, speed=speed)
		except FileNotFoundError:
			filename = ''.join(filter(lambda x: not x.isdigit(), filename))
			return getaudiofromfile(filename, path, defaultpath, settings, volume=volume, speed=speed)
	except exceptions.CouldntDecodeError:
		return 1, np.zeros((0, 2), dtype=np.float32)


def setuphitsound(filenames, beatmappath, skinpath, defaultpath, settings=None):

	bmapindex = 0
	skinindex = 1

	if settings.settings["Use skin's sound samples"]:
		beatmappath = "reeeee"

	for f in filenames[bmapindex]:
		Hitsound.hitsounds[f] = Audio2p(*getaudiofrombeatmap(f, beatmappath, skinpath, defaultpath, settings, volume=settings.settings["Effect volume"]/100))
	for f in filenames[skinindex]:
		Hitsound.hitsounds[f] = Audio2p(*getaudiofromfile(f, skinpath, defaultpath, settings, volume=settings.settings["Effect volume"]/100))

	Hitsound.spinnerbonus = Audio2p(*getaudiofromfile("spinnerbonus", skinpath, defaultpath, settings, volume=settings.settings["Effect volume"]/100))
	Hitsound.miss = Audio2p(*getaudiofromfile("combobreak", skinpath, defaultpath, settings, volume=settings.settings["Effect volume"]/100))
	Hitsound.sectionfail = Audio2p(*getaudiofromfile("sectionfail", skinpath, defaultpath, settings, volume=settings.settings["Effect volume"]/100))
	Hitsound.sectionpass = Audio2p(*getaudiofromfile("sectionpass", skinpath, defaultpath, settings, volume=settings.settings["Effect volume"]/100))

	for x in range(100, 150, 5):
		speed = x/100
		Hitsound.spinnerspin.append(Audio2p(*getaudiofromfile("spinnerspin", skinpath, defaultpath, settings, volume=settings.settings["Effect volume"]/200, speed=speed)))


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
		e = min(int(rendtime / 1000 * song.rate), len(out))
		out = out[:e]
	return out


def apply_offset(song, offset):
	if offset > 0:
		out = np.zeros((len(song.audio) + int(offset / 1000 * song.rate), 2), dtype=song.audio.dtype)
		out[int(offset / 1000 * song.rate):] = song.audio
	else:
		offset = -offset
		out = song.audio[int(offset / 1000 * song.rate):]

	return out


def processaudio(my_info, beatmap, offset, endtime, mods, settings):
	try:
		audioprc(my_info, beatmap, offset, endtime, mods, settings)
	except Exception as e:
		error = repr(e)
		with open("error.txt", "w") as fwrite:  # temporary fix
			fwrite.write(repr(e))
		logging.error("{} from audio\n\n\n".format(error))
		raise


def audioprc(my_info, beatmap, offset, endtime, mods, settings):
	nc = Mod.Nightcore in mods
	addmisssound = not (Mod.Relax in mods or Mod.Autopilot in mods)

	skin_path = settings.skin_path
	default_skinpath = settings.default_path
	beatmap_path = settings.beatmap
	audio_name = beatmap.general["AudioFilename"]

	ccc = time.time()

	try:
		song = Audio2p(*read(os.path.join(beatmap_path, audio_name), settings, volume=settings.settings["Song volume"]/100, speed=settings.timeframe/1000, changepitch=nc))
	except FileNotFoundError:
		raise AudioNotFound()
	song.rate /= settings.timeframe/1000
	song.audio = apply_offset(song, settings.settings["Song delay"])

	filenames = getfilenames(beatmap, settings.settings["Ignore beatmap hitsounds"])
	setuphitsound(filenames, beatmap_path, skin_path, default_skinpath, settings)

	if not addmisssound:
		Hitsound.miss = Audio2p(1, np.zeros((0, 2), dtype=np.float32))

	hitsoundm = HitsoundManager(beatmap)

	print("Done loading", time.time() - ccc)

	for x in range(len(my_info)):

		hitsoundm.updatetimingpoint(my_info, x, song)
		hitsoundm.addhitsound(my_info, x, song)
		hitsoundm.addslidersound(my_info, x, song)
		hitsoundm.addspinnerhitsound(my_info, x, song)
		hitsoundm.addcombobreak(my_info, x, song)
		hitsoundm.addsectionsound(my_info, x, song)

	out = getoffset(offset, endtime, song)

	write(settings.temp + 'audio.mp3', round(song.rate * settings.timeframe/1000), out)


def create_audio(my_info, beatmap_info, offset, endtime, settings, mods):
	beatmap_info = deepcopy(beatmap_info)

	if settings.process >= 1:
		audio_args = (my_info, beatmap_info, offset, endtime, mods, settings,)
		audio = Process(target=processaudio, args=audio_args)
		audio.start()
		return audio
	else:
		processaudio(my_info, beatmap_info, offset, endtime, mods, settings)
		return None
