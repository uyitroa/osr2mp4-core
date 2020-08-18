class BeatmapNotFound(Exception):
	def __repr__(self):
		return "Make sure you chose the right mapset folder and the .osu file is in the mapset folder. If you stored your Songs folder in a different location, click Select Mapset and choose the right mapset folder."


class ReplayNotFound(Exception):
	pass


class AudioNotFound(Exception):
	def __repr__(self):
		return "Make sure the audio file is in the mapset folder or try moving the osr2mp4 folder to somewhere else because the current path might have some special characters."


class GameModeNotSupported(Exception):
	pass


class HarumachiCloverBan(Exception):
	pass


class NoDataReplay(Exception):
	def __repr__(self):
		return "This replay has no cursor data. Make sure you can watch the replay in osu! client and export it again."


class CannotCreateVideo(Exception):
	def __init__(self, msg=None):
		if msg is None:
			self.msg = "Cannot start writing video, make sure your video fourcc codec is correct and supported (https://www.fourcc.org), your output filename has correct video extensions (.mp4, .avi, etc), and your output folder exists."
		else:
			self.msg = msg

	def __repr__(self):
		return self.msg


class WrongFourcc(Exception):
	def __repr__(self):
		return "Wrong codec fourcc. Visit https://www.fourcc.org to find the right video codec."


class FourccIsNotExtension(Exception):
	def __repr__(self):
		return "Video codec is not video file extension (.mp4, .avi, etc...). XVID is a video codec, .mp4 is not."


class LibAvNotFound(Exception):
	def __repr__(self):
		return "To use ffmpeg video writer, you need to download ffmpeg's library here: https://ffmpeg.zeranoe.com/builds/. Select linking shared instead of static, then put all the files from 'bin' folder to osr2mp4 folder (put all files from 'lib' folder to osr2mp4 if you are on macOS)."
