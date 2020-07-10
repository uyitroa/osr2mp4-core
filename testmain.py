from PIL import Image

from osr2mp4.ImageProcess.PrepareFrames.Components.Cursor import prepare_cursor, prepare_cursormiddle
from osr2mp4.ImageProcess.PrepareFrames.Components.PlayingGrade import prepare_playinggrade
from osr2mp4.ImageProcess.PrepareFrames.HitObjects.Circles import prepare_circle

from osr2mp4.InfoProcessor import Updater

from osr2mp4.ImageProcess.Objects.Scores.PPCounter import PPCounter
from osr2mp4.osr2mp4 import Osr2mp4


class DummyTest:

	def __init__(*args, **kwargs):
		pass

	def __call__(self, *args, **kwargs):
		return self

	def __getattr__(self, *args, **kwargs):
		return self


class DummyFrameObjects:
	def __init__(self):
		self.cursormiddle = DummyTest()
		self.cursor = DummyTest()
		self.cursor_trail = DummyTest()

		self.scoreentry = DummyTest()

		self.inputoverlayBG = DummyTest()
		self.key1 = DummyTest()
		self.key2 = DummyTest()
		self.mouse1 = DummyTest()
		self.mouse2 = DummyTest()

		self.accuracy = DummyTest()
		self.timepie = DummyTest()
		self.playinggrade = DummyTest()
		self.hitresult = DummyTest()
		self.spinbonus = DummyTest()
		self.combocounter = DummyTest()
		self.scorecounter = DummyTest()

		self.urbar = DummyTest()

		self.followpoints = DummyTest()

		self.hitcirclenumber = DummyTest()
		self.circle = DummyTest()
		self.slider = DummyTest()
		self.spinner = DummyTest()
		self.hitobjmanager = DummyTest()

		self.background = DummyTest()
		self.sections = DummyTest()
		self.scorebarbg = DummyTest()
		self.scorebar = DummyTest()
		self.arrowwarning = DummyTest()

		self.scoreboard = DummyTest()

		self.rankingpanel = DummyTest()
		self.rankinghitresults = DummyTest()
		self.rankingtitle = DummyTest()
		self.rankingcombo = DummyTest()
		self.rankingaccuracy = DummyTest()
		self.rankinggrade = DummyTest()
		self.menuback = DummyTest()
		self.modicons = DummyTest()
		self.rankingreplay = DummyTest()
		self.rankinggraph = DummyTest()
		self.ppcounter = DummyTest()


def saveimage(listimg, filename="0", pdf=False):
	for counter, l in enumerate(listimg):
		if type(l).__name__ == "list":
			saveimage(l, filename + str(counter), pdf=pdf)
		else:
			if not pdf:
				l.save(filename + str(counter) + ".png")
			else:
				savepdf(listimg, filename + ".pdf")


def savepdf(listimg, filename):
	for i in range(len(listimg)):
		if listimg[i].mode == "RGBA":
			rgb = Image.new('RGB', listimg[i].size, (255, 255, 255))  # white background
			rgb.paste(listimg[i], mask=listimg[i].split()[3])
			listimg[i] = rgb
	listimg[0].save(filename, save_all=True, append_images=listimg[1:])


def testpp(components, osr2mp4):
	components.ppcounter = PPCounter(osr2mp4.settings)
	updater = Updater(osr2mp4.resultinfo, components, osr2mp4.settings, osr2mp4.replay_info.mod_combination,
	                  osr2mp4.beatmap_file)
	for x in range(200, len(osr2mp4.beatmap.hitobjects)):
		updater.update(osr2mp4.beatmap.hitobjects[x]["time"])
		print(components.ppcounter.pp)


def testcircle(osr2mp4):
	a = prepare_circle(osr2mp4.beatmap, osr2mp4.settings.scale, osr2mp4.settings, False)
	saveimage(a[0][0])


def testplayinggrade(osr2mp4):
	a = prepare_playinggrade(osr2mp4.settings.scale, osr2mp4.settings)
	saveimage(a[0], pdf=True)


def main():
	osr2mp4 = Osr2mp4(filedata="/Users/yuitora./PycharmProjects/osr2mp4-core/osr2mp4/config.json",
	                  filesettings="/Users/yuitora./PycharmProjects/osr2mp4-core/osr2mp4/settings.json", logtofile=True)
	osr2mp4.analyse_replay()
	components = DummyFrameObjects()
	# testpp(components, osr2mp4)
	# testcircle(osr2mp4)
	# testplayinggrade(osr2mp4)
	b = prepare_cursor(osr2mp4.settings.scale, osr2mp4.settings)
	print(b[1])
	a = prepare_cursormiddle(osr2mp4.settings.scale, osr2mp4.settings, default=b[1])
	print(a[1])




if __name__ == '__main__':
	main()
