class Dummy:

	def __init__(*args, **kwargs):
		pass

	def __call__(self, *args, **kwargs):
		return self

	def __getattr__(self, *args, **kwargs):
		return self


class FrameObjects:
	def __init__(self):
		self.cursormiddle = Dummy()
		self.cursor = Dummy()
		self.cursor_trail = Dummy()

		self.scoreentry = Dummy()

		self.inputoverlayBG = Dummy()
		self.key1 = Dummy()
		self.key2 = Dummy()
		self.mouse1 = Dummy()
		self.mouse2 = Dummy()

		self.accuracy = Dummy()
		self.timepie = Dummy()
		self.playinggrade = Dummy()
		self.hitresult = Dummy()
		self.spinbonus = Dummy()
		self.combocounter = Dummy()
		self.scorecounter = Dummy()

		self.urbar = Dummy()

		self.followpoints = Dummy()

		self.hitcirclenumber = Dummy()
		self.circle = Dummy()
		self.slider = Dummy()
		self.spinner = Dummy()
		self.hitobjmanager = Dummy()

		self.background = Dummy()
		self.sections = Dummy()
		self.scorebarbg = Dummy()
		self.scorebar = Dummy()
		self.arrowwarning = Dummy()

		self.scoreboard = Dummy()

		self.rankingpanel = Dummy()
		self.rankinghitresults = Dummy()
		self.rankingtitle = Dummy()
		self.rankingcombo = Dummy()
		self.rankingaccuracy = Dummy()
		self.rankinggrade = Dummy()
		self.menuback = Dummy()
		self.modicons = Dummy()
		self.rankingreplay = Dummy()
		self.rankinggraph = Dummy()
		self.ppcounter = Dummy()
