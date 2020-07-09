


class FrameObjects:
	def __init__(self):
		self.cursormiddle = Cursor()
		self.cursor = Cursor()
		self.cursor_trail = Cursortrail()
		# self.lifegraph = LifeGraph()

		self.scoreentry = ScoreEntry()

		self.inputoverlayBG = InputOverlayBG()
		self.key1 = InputOverlay()
		self.key2 = InputOverlay()
		self.mouse1 = InputOverlay()
		self.mouse2 = InputOverlay()

		self.accuracy = Accuracy()
		self.timepie = TimePie()
		self.playinggrade = PlayingGrade()
		self.hitresult = HitResult()
		self.spinbonus = SpinBonusScore()
		self.combocounter = ComboCounter()
		self.scorecounter = ScoreCounter()

		self.urbar = URBar()

		self.followpoints = FollowPointsManager()

		self.hitcirclenumber = Number()
		self.circle = CircleManager()
		self.slider = SliderManager()
		self.spinner = SpinnerManager(), settings, check)
		self.hitobjmanager = HitObjectManager()

		self.background = Background()
		self.sections = Sections()
		self.scorebarbg = ScorebarBG()
		self.scorebar = Scorebar()
		self.arrowwarning = ArrowWarning()

		self.scoreboard = Scoreboard()

		self.rankingpanel = RankingPanel()
		self.rankinghitresults = RankingHitresults()
		self.rankingtitle = RankingTitle()
		self.rankingcombo = RankingCombo()
		self.rankingaccuracy = RankingAccuracy()
		self.rankinggrade = RankingGrade()
		self.menuback = Menuback()
		self.modicons = ModIcons()
		self.rankingreplay = RankingReplay()
		self.rankinggraph = RankingGraph()
		self.ppcounter = PPCounter()
