from osr2mp4.ImageProcess.Objects.Components.PlayingModIcons import PlayingModIcons
from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.ModIcons import prepare_modicons

from osr2mp4.ImageProcess.PrepareFrames.RankingScreens.RankingUR import prepare_rankingur
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
			from PIL import Image
			rgb = Image.new('RGB', listimg[i].size, (255, 255, 255))  # white background
			rgb.paste(listimg[i], mask=listimg[i].split()[3])
			listimg[i] = rgb
	listimg[0].save(filename, save_all=True, append_images=listimg[1:])


def testpp(components, osr2mp4):
	from osr2mp4.ImageProcess.Objects.Scores.PPCounter import PPCounter
	from osr2mp4.InfoProcessor import Updater

	components.ppcounter = PPCounter(osr2mp4.settings)
	updater = Updater(osr2mp4.resultinfo, components, osr2mp4.settings, osr2mp4.replay_info.mod_combination,
	                  osr2mp4.beatmap_file)
	for x in range(200, len(osr2mp4.beatmap.hitobjects)):
		updater.update(osr2mp4.beatmap.hitobjects[x]["time"])
		print(components.ppcounter.pp)


def testcircle(osr2mp4):
	from osr2mp4.ImageProcess.PrepareFrames.HitObjects.Circles import prepare_circle
	a = prepare_circle(osr2mp4.beatmap, osr2mp4.settings.scale, osr2mp4.settings, False)
	saveimage(a[0][0])


def testplayinggrade(osr2mp4):
	from osr2mp4.ImageProcess.PrepareFrames.Components.PlayingGrade import prepare_playinggrade
	a = prepare_playinggrade(osr2mp4.settings.scale, osr2mp4.settings)
	saveimage(a[0], pdf=True)


def drawcircle(background, components, osr2mp4, skin):
	from osr2mp4.Parser.osuparser import read_file
	from osr2mp4.ImageProcess.PrepareFrames.HitObjects.Circles import prepare_circle
	from osr2mp4.ImageProcess.Objects.HitObjects.CircleNumber import Number
	from osr2mp4.ImageProcess.PrepareFrames.HitObjects.CircleNumber import prepare_hitcirclenumber
	from osr2mp4.ImageProcess.Objects.HitObjects.Circles import CircleManager

	b = read_file("test.osu", osr2mp4.settings.scale, skin.colours, False)
	print(b)
	frames = prepare_circle(osr2mp4.beatmap, osr2mp4.settings.playfieldscale, osr2mp4.settings, False)
	components.hitcirclenumber = Number(
		prepare_hitcirclenumber(osr2mp4.beatmap.diff, osr2mp4.settings.playfieldscale, osr2mp4.settings), skin.fonts)
	components.circle = CircleManager(frames, 800, components.hitcirclenumber, osr2mp4.settings)
	hitobject = osr2mp4.beatmap.hitobjects[40]
	hitobject["combo_number"] = 11
	components.circle.add_circle(hitobject, hitobject["x"], hitobject["y"], hitobject["time"] - 10)
	components.circle.add_to_frame(background, str(hitobject["id"]) + "c", 0)
	background.save("test.png")


def drawpp(components, osr2mp4):
	from osr2mp4.ImageProcess.Objects.Scores.PPCounter import PPCounter
	from PIL import Image

	background = Image.open("pppp.png")
	osr2mp4.settings.settings["Enable PP counter"] = True
	components.ppcounter = PPCounter(osr2mp4.settings)
	components.ppcounter.set(727.27)
	components.ppcounter.add_to_frame(background)
	background.save("test.png")


def main():
	from PIL import Image
	from osr2mp4.Parser.skinparser import Skin

	osr2mp4 = Osr2mp4(filedata="osr2mp4/config.json", filesettings="osr2mp4/settings.json", filepp="osr2mp4/ppsettings.json", logtofile=True)
	osr2mp4.analyse_replay()
	print(osr2mp4.resultinfo[-1].accuracy)
	print(osr2mp4.replay_info.number_300s, osr2mp4.replay_info.number_100s, osr2mp4.replay_info.number_50s, osr2mp4.replay_info.misses)
	# components = DummyFrameObjects()
	# background = Image.open("../osr2mp4-app/osr2mp4app/res/pppp.png")
	# #
	# # drawpp(components, osr2mp4)
	# a = prepare_modicons(osr2mp4.settings.scale, osr2mp4.settings)
	# f = PlayingModIcons(a, osr2mp4.replay_info, osr2mp4.settings)
	# f.add_to_frame(background)
	# background.save("test.png")


if __name__ == '__main__':
	main()
