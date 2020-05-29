from ..ImageProcess.Objects.RankingScreens.Menuback import Menuback
from ..ImageProcess.Objects.RankingScreens.ModIcons import ModIcons
from ..ImageProcess.Objects.RankingScreens.RankingAccuracy import RankingAccuracy
from ..ImageProcess.Objects.RankingScreens.RankingCombo import RankingCombo
from ..ImageProcess.Objects.RankingScreens.RankingGrade import RankingGrade
from ..ImageProcess.Objects.RankingScreens.RankingGraph import RankingGraph
from ..ImageProcess.Objects.RankingScreens.RankingHitresults import RankingHitresults
from ..ImageProcess.Objects.RankingScreens.RankingPanel import RankingPanel
from ..ImageProcess.Objects.Components.Scoreboard import Scoreboard
from ..ImageProcess.Objects.Components.ArrowWarning import ArrowWarning
from ..ImageProcess.Objects.Components.Background import Background
from ..ImageProcess.Objects.Components.Scorebar import Scorebar
from ..ImageProcess.Objects.Components.ScorebarBG import ScorebarBG
from ..ImageProcess.Objects.Components.Sections import Sections
from ..ImageProcess.Objects.RankingScreens.RankingReplay import RankingReplay
from ..ImageProcess.Objects.RankingScreens.RankingTitle import RankingTitle
from ..ImageProcess.Objects.Scores.ScoreNumbers import ScoreNumbers
from ..ImageProcess.Objects.Components.Followpoints import FollowPointsManager
from ..ImageProcess.Objects.Components.TimePie import TimePie
from ..ImageProcess.Objects.HitObjects.CircleNumber import Number
from ..ImageProcess.Objects.HitObjects.Slider import SliderManager
from ..ImageProcess.Objects.HitObjects.Spinner import SpinnerManager
from ..ImageProcess.Objects.Scores.Accuracy import Accuracy
from ..ImageProcess.Objects.Scores.ComboCounter import ComboCounter
from ..ImageProcess.Objects.Scores.Hitresult import HitResult
from ..ImageProcess.Objects.Scores.ScoreCounter import ScoreCounter
from ..ImageProcess.Objects.HitObjects.Circles import CircleManager
from ..ImageProcess.Objects.HitObjects.Manager import HitObjectManager
from ..ImageProcess.Objects.Components.Button import InputOverlay, InputOverlayBG, ScoreEntry
from ..ImageProcess.Objects.Components.Cursor import Cursor, Cursortrail
from ..ImageProcess.Objects.Scores.SpinBonusScore import SpinBonusScore
from ..ImageProcess.Objects.Scores.URBar import URBar
from ..ImageProcess.PrepareFrames.Components.ArrowWarning import prepare_arrowwarning
from ..ImageProcess.PrepareFrames.Components.Button import prepare_scoreentry, prepare_inputoverlaybg, \
	prepare_inputoverlay
from ..ImageProcess.PrepareFrames.Components.Cursor import prepare_cursor, prepare_cursortrail, prepare_cursormiddle
from ..ImageProcess.PrepareFrames.Components.Followpoints import prepare_fpmanager
from ..ImageProcess.PrepareFrames.Components.Background import prepare_background
from ..ImageProcess.PrepareFrames.RankingScreens.BackButton import prepare_menuback
from ..ImageProcess.PrepareFrames.RankingScreens.ModIcons import prepare_modicons
from ..ImageProcess.PrepareFrames.RankingScreens.RankingAccuracy import prepare_rankingaccuracy
from ..ImageProcess.PrepareFrames.RankingScreens.RankingCombo import prepare_rankingcombo
from ..ImageProcess.PrepareFrames.RankingScreens.RankingGrade import prepare_rankinggrade
from ..ImageProcess.PrepareFrames.RankingScreens.RankingGraph import prepare_rankinggraph
from ..ImageProcess.PrepareFrames.RankingScreens.RankingHitresults import prepare_rankinghitresults
from ..ImageProcess.PrepareFrames.RankingScreens.RankingPanel import prepare_rankingpanel
from ..ImageProcess.PrepareFrames.Components.Scorebar import prepare_scorebar
from ..ImageProcess.PrepareFrames.Components.ScorebarBG import prepare_scorebarbg
from ..ImageProcess.PrepareFrames.Components.Scoreboard import prepare_scoreboard
from ..ImageProcess.PrepareFrames.Components.Sections import prepare_sections
from ..ImageProcess.PrepareFrames.Effects.ScoreboardEffect import prepare_scoreboardeffect
from ..ImageProcess.PrepareFrames.HitObjects.CircleNumber import prepare_hitcirclenumber
from ..ImageProcess.PrepareFrames.HitObjects.Circles import prepare_circle, calculate_ar
from ..ImageProcess.PrepareFrames.HitObjects.Slider import prepare_slider
from ..ImageProcess.PrepareFrames.HitObjects.Spinner import prepare_spinner
from ..ImageProcess.PrepareFrames.RankingScreens.RankingReplay import prepare_rankingreplay
from ..ImageProcess.PrepareFrames.RankingScreens.RankingScore import prepare_rankingscorecounter
from ..ImageProcess.PrepareFrames.RankingScreens.RankingTitle import prepare_rankingtitle
from ..ImageProcess.PrepareFrames.Scores.Accuracy import prepare_accuracy
from ..ImageProcess.PrepareFrames.Scores.ComboCounter import prepare_combo
from ..ImageProcess.PrepareFrames.Scores.Hitresult import prepare_hitresults
from ..ImageProcess.PrepareFrames.Scores.ScoreCounter import prepare_scorecounter
from ..ImageProcess.PrepareFrames.Scores.Scoreentry import prepare_scoreboardscore
from ..ImageProcess.PrepareFrames.Scores.SpinBonusScore import prepare_spinbonus
from ..ImageProcess.PrepareFrames.Scores.URBar import prepare_bar
from ..global_var import Settings, Paths, GameplaySettings


class PreparedFrames:
	def __init__(self, skin, check, beatmap, hd):
		if GameplaySettings.settings["Automatic cursor size"]:
			circlescale = 4/beatmap.diff["CircleSize"]
			GameplaySettings.settings["Cursor size"] *= circlescale
		self.cursor, default = prepare_cursor(Settings.scale * GameplaySettings.settings["Cursor size"])
		self.cursormiddle, self.continuous = prepare_cursormiddle(Settings.scale * GameplaySettings.settings["Cursor size"], default)
		self.cursor_trail = prepare_cursortrail(Settings.scale * GameplaySettings.settings["Cursor size"], self.continuous)

		self.scoreentry = prepare_scoreentry(Settings.scale, skin.colours["InputOverlayText"])
		self.inputoverlayBG = prepare_inputoverlaybg(Settings.scale)
		self.key = prepare_inputoverlay(Settings.scale, [255, 220, 20], 2)
		self.mouse = prepare_inputoverlay(Settings.scale, [220, 0, 220], 1)

		self.scorenumbers = ScoreNumbers(Settings.scale)
		self.hitcirclenumber = prepare_hitcirclenumber(beatmap.diff, Settings.playfieldscale)

		self.accuracy = prepare_accuracy(self.scorenumbers)
		self.combocounter = prepare_combo(self.scorenumbers)
		self.hitresult = prepare_hitresults(Settings.scale, beatmap)
		self.spinbonus = prepare_spinbonus(self.scorenumbers)
		self.scorecounter = prepare_scorecounter(self.scorenumbers)

		self.urbar = prepare_bar(Settings.scale * GameplaySettings.settings["Score meter size"], check.scorewindow)

		self.fpmanager = prepare_fpmanager(Settings.playfieldscale)

		self.circle = prepare_circle(beatmap, Settings.playfieldscale, skin, hd)
		self.slider = prepare_slider(beatmap.diff, Settings.playfieldscale, skin)
		self.spinner = prepare_spinner(Settings.playfieldscale)

		self.bg = prepare_background(Paths.beatmap + beatmap.bg[2])

		self.sections = prepare_sections(Settings.scale)
		self.scorebarbg = prepare_scorebarbg(Settings.scale, self.bg)
		self.scorebar = prepare_scorebar(Settings.scale)
		self.arrowwarning = prepare_arrowwarning(Settings.scale)

		self.scoreboardscore = prepare_scoreboardscore(Settings.scale)
		self.scoreboard = prepare_scoreboard(Settings.scale)
		self.scoreboardeffect = prepare_scoreboardeffect(Settings.scale)

		self.rankingpanel = prepare_rankingpanel(Settings.scale, self.bg)
		self.rankinghitresults = prepare_rankinghitresults(Settings.scale)
		self.rankingscore = prepare_rankingscorecounter(self.scorenumbers)
		self.rankinggrades = prepare_rankinggrade(Settings.scale)
		self.rankingtitle = prepare_rankingtitle(Settings.scale)
		self.rankingcombo = prepare_rankingcombo(Settings.scale)
		self.rankingaccuracy = prepare_rankingaccuracy(Settings.scale)
		self.menuback = prepare_menuback(Settings.scale)
		self.modicons = prepare_modicons(Settings.scale)
		self.rankingreplay = prepare_rankingreplay(Settings.scale)
		self.rankinggraph = prepare_rankinggraph(Settings.scale)


class FrameObjects:
	def __init__(self, frames, skin, beatmap, replay_info, check, hd):
		opacity_interval, timepreempt, _ = calculate_ar(beatmap.diff["ApproachRate"])
		rankinggap = 0

		self.cursormiddle = Cursor(frames.cursormiddle)
		self.cursor = Cursor(frames.cursor)
		self.cursor_trail = Cursortrail(frames.cursor_trail, frames.continuous)
		# self.lifegraph = LifeGraph(skin_path + "scorebarbg-colour")

		self.scoreentry = ScoreEntry(frames.scoreentry)

		self.inputoverlayBG = InputOverlayBG(frames.inputoverlayBG)
		self.key1 = InputOverlay(frames.key, self.scoreentry)
		self.key2 = InputOverlay(frames.key, self.scoreentry)
		self.mouse1 = InputOverlay(frames.mouse, self.scoreentry)
		self.mouse2 = InputOverlay(frames.mouse, self.scoreentry)

		self.accuracy = Accuracy(frames.accuracy, skin.fonts["ScoreOverlap"])
		self.timepie = TimePie(self.accuracy, beatmap.start_time, beatmap.end_time, frames.scorebarbg)
		self.hitresult = HitResult(frames.hitresult)
		self.spinbonus = SpinBonusScore(frames.spinbonus, skin.fonts["ScoreOverlap"])
		self.combocounter = ComboCounter(frames.combocounter, skin.fonts["ScoreOverlap"])
		self.scorecounter = ScoreCounter(frames.scorecounter, beatmap.diff, skin.fonts["ScoreOverlap"])

		self.urbar = URBar(frames.urbar)

		self.followpoints = FollowPointsManager(frames.fpmanager)

		self.hitcirclenumber = Number(frames.hitcirclenumber, skin.fonts)
		self.circle = CircleManager(frames.circle, timepreempt, self.hitcirclenumber)
		self.slider = SliderManager(frames.slider, beatmap.diff, skin, hd)
		self.spinner = SpinnerManager(frames.spinner)
		self.hitobjmanager = HitObjectManager(self.circle, self.slider, self.spinner, check.scorewindow[2])

		self.background = Background(frames.bg, beatmap.start_time - timepreempt)
		self.sections = Sections(frames.sections)
		self.scorebarbg = ScorebarBG(frames.scorebarbg, beatmap.start_time - timepreempt)
		self.scorebar = Scorebar(frames.scorebar, beatmap)
		self.arrowwarning = ArrowWarning(frames.arrowwarning)

		self.scoreboard = Scoreboard(frames.scoreboard, frames.scoreboardscore, frames.scoreboardeffect, replay_info, beatmap)

		self.rankingpanel = RankingPanel(frames.rankingpanel)
		self.rankinghitresults = RankingHitresults(frames.rankinghitresults, replay_info, frames.rankingscore, rankinggap)
		self.rankingtitle = RankingTitle(frames.rankingtitle, replay_info, beatmap)
		self.rankingcombo = RankingCombo(frames.rankingcombo, replay_info, frames.rankingscore, rankinggap)
		self.rankingaccuracy = RankingAccuracy(frames.rankingaccuracy, replay_info, frames.rankingscore, rankinggap)
		self.rankinggrade = RankingGrade(replay_info, frames.rankinggrades, rankinggap)
		self.menuback = Menuback(frames.menuback, skin)
		self.modicons = ModIcons(frames.modicons, replay_info)
		self.rankingreplay = RankingReplay(frames.rankingreplay)
		self.rankinggraph = RankingGraph(frames.rankinggraph, replay_info)
